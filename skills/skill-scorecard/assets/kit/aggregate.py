"""Pool caliper results + check metrics into summary-<tags>.json.

Usage (from the eval dir): python3 aggregate.py <tag> [<tag> ...]
Reads results-<tag>-<arm>.json and metrics-<tag>.jsonl for every tag; unusable attempts
(infra_error, timeout, judge_error) are excluded from every rate.
"""
import json
import math
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

import yaml

TAGS = sys.argv[1:]
ARMS = ["noskill", "skill", "always"]
meta = json.loads(Path("meta.json").read_text())
RISKY = {k for k, t in meta["tasks"].items() if t.get("risky")}

# Task name -> key, from every spec's `assert: checks/<key>.py`.
KEY = {}
for spec in Path(".").glob("*.eval.yaml"):
    for t in yaml.safe_load(spec.read_text())["tasks"]:
        KEY[t["name"]] = Path(t["assert"]).stem


def wilson(s, n, z=1.96):
    if not n:
        return (None, None)
    p, d = s / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


def fisher(a, b, c, d):
    """Two-sided Fisher exact p for the 2x2 table [[a, b], [c, d]]."""
    n1, n2, k = a + b, c + d, a + c
    pmf = lambda x: math.comb(n1, x) * math.comb(n2, k - x) / math.comb(n1 + n2, k)
    p0 = pmf(a)
    return min(1.0, sum(pmf(x) for x in range(max(0, k - n2), min(k, n1) + 1) if pmf(x) <= p0 + 1e-12))


metrics = defaultdict(list)
for tag in TAGS:
    mp = Path(f"metrics-{tag}.jsonl")
    for line in mp.read_text().splitlines() if mp.exists() else []:
        d = json.loads(line)
        metrics[(d["arm"], d["task"])].append(d)

out = {"tags": TAGS, "arms": {}}
for arm in ARMS:
    pooled = defaultdict(list)
    for tag in TAGS:
        p = Path(f"results-{tag}-{arm}.json")
        if p.exists():
            for t in json.loads(p.read_text())["task_results"]:
                pooled[KEY[t["task_name"]]].extend(t["attempts"])
    if not pooled:
        continue
    A = {"tasks": {}, "passes": 0, "usable": 0, "unusable": 0, "act_fired": 0, "act_obs": 0}
    tokens, out_tokens, wall = [], [], []
    for key, attempts in pooled.items():
        T = {"passes": 0, "usable": 0, "fails": []}
        for a in attempts:
            oc = a.get("outcome")
            if oc in ("pass", "task_fail", "cheat"):
                T["usable"] += 1
                T["passes"] += oc == "pass"
                if oc != "pass":
                    T["fails"].append((a.get("assert_evidence") or oc)[:160])
            else:
                A["unusable"] += 1
                continue
            if a.get("activated") is not None:
                A["act_obs"] += 1
                A["act_fired"] += meta["skill_name"] in (a.get("activated") or [])
            u = a.get("usage") or {}
            tot = sum(u.get(k) or 0 for k in ("input_tokens", "output_tokens", "cache_read_tokens", "cache_creation_tokens"))
            if tot:
                tokens.append(tot)
                out_tokens.append(u.get("output_tokens") or 0)
            wall.append(a.get("duration_seconds") or 0)
        ms = metrics.get((arm, key), [])
        T["rate"] = T["passes"] / T["usable"] if T["usable"] else None
        T["src_added_median"] = st.median([m["src_added"] for m in ms]) if ms else None
        T["wrote_test"] = sum(m.get("wrote_test", False) for m in ms)
        T["new_deps"] = sum(bool(m.get("dep_files_changed")) for m in ms)
        A["passes"] += T["passes"]
        A["usable"] += T["usable"]
        A["tasks"][key] = T
    allm = [m for (a_, _), v in metrics.items() if a_ == arm for m in v]
    risky = [m for m in allm if m["task"] in RISKY]
    A["rate"] = A["passes"] / A["usable"] if A["usable"] else None
    A["ci"] = wilson(A["passes"], A["usable"])
    A["src_added_total_mean"] = round(st.mean(m["src_added"] for m in allm), 1) if allm else None
    A["risky_test_rate"] = sum(m.get("wrote_test", False) for m in risky) / len(risky) if risky else None
    A["tokens_mean"] = round(st.mean(tokens)) if tokens else None
    A["out_tokens_mean"] = round(st.mean(out_tokens)) if out_tokens else None
    A["wall_mean"] = round(st.mean(wall), 1) if wall else None
    A["activation_rate"] = A["act_fired"] / A["act_obs"] if A["act_obs"] else None
    A["min_usable"] = min(t["usable"] for t in A["tasks"].values())
    out["arms"][arm] = A

# Per-arm and per-task significance against the no-skill arm.
B = out["arms"].get("noskill")
out["p_vs_noskill"], out["flipped"] = {}, []
for arm in ("skill", "always"):
    X = out["arms"].get(arm)
    if not (B and X):
        continue
    out["p_vs_noskill"][arm] = round(fisher(X["passes"], X["usable"] - X["passes"], B["passes"], B["usable"] - B["passes"]), 4)
    for key, t in X["tasks"].items():
        b = B["tasks"].get(key)
        if b and t["usable"] and b["usable"]:
            p = fisher(t["passes"], t["usable"] - t["passes"], b["passes"], b["usable"] - b["passes"])
            if p < 0.05:
                out["flipped"].append({"arm": arm, "task": key, "p": round(p, 5),
                                       "arm_score": f"{t['passes']}/{t['usable']}", "noskill_score": f"{b['passes']}/{b['usable']}",
                                       "direction": "win" if t["rate"] > b["rate"] else "loss"})

name = "summary-" + "+".join(TAGS) + ".json"
Path(name).write_text(json.dumps(out, indent=2))

for arm, x in out["arms"].items():
    print(f"{arm:8} pass {x['passes']}/{x['usable']} = {x['rate']:.0%} CI{x['ci']}  unusable={x['unusable']}  "
          f"min n/task={x['min_usable']}  act={x['activation_rate']}  loc={x['src_added_total_mean']}  "
          f"risky_test={x['risky_test_rate']}  tok={x['tokens_mean']}  out={x['out_tokens_mean']}  wall={x['wall_mean']}s")
print("p vs noskill:", out["p_vs_noskill"])
for f in out["flipped"]:
    print(f"FLIPPED  {f['arm']:7} {f['task']:12} {f['direction']:4} {f['arm_score']} vs {f['noskill_score']}  p={f['p']}")
tasks = list(dict.fromkeys(k for a in out["arms"].values() for k in a["tasks"]))
print(f"\n{'task':12} " + "  ".join(f"{a:>22}" for a in out["arms"]))
for k in tasks:
    print(f"{k:12} " + "  ".join(
        (f"{t['passes']}/{t['usable']} loc~{t['src_added_median']} t{t['wrote_test']}" if (t := out['arms'][a]['tasks'].get(k)) else "-").rjust(22)
        for a in out["arms"]))
print(f"\n-> {name}")
