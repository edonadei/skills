"""Build the eval's fixtures from a finished ponytail scorecard folder.

    python3 build_fixtures.py <ponytail-eval-dir>

fixtures/finished/  the real ponytail run, stopped after step 5 (copy.json holds only the claims)
fixtures/harmful/   the same run, with the always-on arm made clearly worse (verdict must be BAD)
fixtures/authfail/  a step-4 smoke run where every attempt died on an expired login
fixtures/safe-sql/  a small skill to evaluate from scratch, shipped with a SessionStart hook

Results are stripped to what the aggregator and the report read.
"""
import json
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
HERE = Path(__file__).parent
FIX = HERE / "fixtures"
EXAMPLE = HERE.parent.parent / "skills/skill-scorecard/assets/example"
TAGS = ["k5", "r2", "r3", "r4", "r5"]
ARM = {"noskill": "noskill", "skill": "skill", "plugin": "always"}


def strip(attempt):
    keep = {k: attempt.get(k) for k in ("attempt", "outcome", "duration_seconds", "usage", "activated",
                                        "assert_passed", "assert_evidence")}
    keep["output"] = (attempt.get("output") or "")[-1500:]
    return keep


def write_results(dst, mutate=None):
    for tag in TAGS:
        for src_arm, arm in ARM.items():
            p = SRC / f"results-{tag}-{src_arm}.json"
            if not p.exists():
                continue
            r = json.loads(p.read_text())
            tasks = [{"task_name": t["task_name"], "attempts": [strip(a) for a in t["attempts"]]} for t in r["task_results"]]
            if mutate:
                mutate(arm, tasks)
            (dst / f"results-{tag}-{arm}.json").write_text(json.dumps({"task_results": tasks}))
        m = SRC / f"metrics-{tag}.jsonl"
        if m.exists():
            lines = [json.loads(l) for l in m.read_text().splitlines()]
            out = []
            for d in lines:
                d["arm"] = ARM.get(d["arm"], d["arm"])
                d.pop("workdir", None)
                out.append(json.dumps(d))
            (dst / f"metrics-{tag}.jsonl").write_text("\n".join(out) + "\n")


def claims_only(copy):
    return {"claims": [{"claim": c["claim"], "readme": c["readme"], "measured": "", "ok": "", "note": "", "short": ""}
                       for c in copy["claims"]]}


def base(dst, skill_md, meta):
    if dst.exists():
        shutil.rmtree(dst)
    (dst / "report").mkdir(parents=True)
    shutil.copytree(SRC / "fixtures", dst / "fixtures", ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    shutil.copytree(SRC / "checks", dst / "checks", ignore=shutil.ignore_patterns("__pycache__", "_common.py", "setup.sh"))
    shutil.copy(skill_md, dst / "SKILL.md")
    (dst / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    shutil.copy(SRC / "ponytail.eval.yaml", dst / "scorecard.eval.yaml")
    shutil.copy(SRC / "ponytail-hard.eval.yaml", dst / "hard.eval.yaml")


meta = json.loads((EXAMPLE / "meta.json").read_text())
copy = json.loads((EXAMPLE / "copy.json").read_text())

# finished: the real run, at the end of step 5.
d = FIX / "finished"
base(d, SRC / "SKILL.md", meta)
write_results(d)
(d / "report/copy.json").write_text(json.dumps(claims_only(copy), indent=2, ensure_ascii=False))

# harmful: the always-on arm fails most attempts on six tasks the baseline passes.
HURT = {"Money split": "AssertionError: 10000 cents in 3 installments sums to 9999 (cents lost/created): [3333, 3333, 3333]",
        "One-liner search": "AssertionError: '_' treated as a wildcard: q=n_l -> ['ann_lee', 'annalee']",
        "Multi-site": "AssertionError: breaks on the existing production database (old schema): no such column: deleted_at",
        "Cache with": "AssertionError: served a rate older than an hour",
        "Feature with money": "AssertionError: fixed discount larger than the cart must floor at 0, got {'ok': -1240}",
        "Adversarial — brute": "AssertionError: lock must lift after 15 minutes, got 429"}


def make_worse(arm, tasks):
    if arm != "always":
        return
    for t in tasks:
        why = next((w for h, w in HURT.items() if t["task_name"].startswith(h)), None)
        if why:
            for i, a in enumerate(t["attempts"]):
                if a["outcome"] == "pass" and i % 5 != 4:
                    a["outcome"] = "task_fail"
                    a["assert_passed"] = False
                    a["assert_evidence"] = why


d = FIX / "harmful"
hmeta = {**meta, "skill_name": "turbo-dev", "skill_repo": "https://github.com/example/turbo-dev",
         "skill_path": "SKILL.md", "commit": "4b1d2c9e0f3a5b7c9d1e2f3a4b5c6d7e8f9a0b1c"}
base(d, SRC / "SKILL.md", hmeta)
for spec in ("scorecard.eval.yaml", "hard.eval.yaml"):
    (d / spec).write_text((d / spec).read_text().replace("Ponytail (DietrichGebert/ponytail @ 16352ac)", "turbo-dev @ 4b1d2c9")
                          .replace("ponytail", "turbo-dev"))
(d / "SKILL.md").write_text("---\nname: turbo-dev\ndescription: Ship faster. Use on any coding task.\n---\n\n"
                            "Move fast. Skip reading code you are not changing. Prefer the shortest diff. "
                            "Skip tests unless asked.\n")
write_results(d, make_worse)
(d / "report/copy.json").write_text(json.dumps({"claims": [
    {"claim": "More tasks solved", "readme": "+20%", "measured": "", "ok": "", "note": "", "short": ""},
    {"claim": "Faster", "readme": "2× faster", "measured": "", "ok": "", "note": "", "short": ""},
    {"claim": "Less code", "readme": "−50%", "measured": "", "ok": "", "note": "", "short": ""},
]}, indent=2, ensure_ascii=False))

# authfail: step 4 smoke run, every attempt an expired login.
d = FIX / "authfail"
base(d, SRC / "SKILL.md", meta)
names = [t["task_name"] for t in json.loads((SRC / "results-k5-noskill.json").read_text())["task_results"]]
msg = "Failed to authenticate: OAuth token revoked. Please log in again or contact your administrator."
for arm in ("noskill", "skill", "always"):
    tasks = [{"task_name": n, "attempts": [{"attempt": 1, "outcome": "infra_error", "duration_seconds": 4.8,
                                            "usage": None, "activated": None, "assert_passed": False,
                                            "assert_evidence": "harness exited 1", "output": msg}]} for n in names]
    (d / f"results-k1-{arm}.json").write_text(json.dumps({"task_results": tasks}))
    (d / f"run-k1-{arm}.log").write_text(
        f"CALIPER · ponytail · k=1 · claude-code · claude-sonnet-5-5\n"
        + "".join(f"⊘ {n} · attempt 1: infra_error\n" for n in names)
        + f"⊘ {len(names)} unusable ({len(names)} infra_error) — excluded from the score\n"
        + f"output: {msg}\nError: No attempt was usable ({len(names)} infra_error) — the run measured nothing.\n")
(d / "report/copy.json").write_text(json.dumps(claims_only(copy), indent=2, ensure_ascii=False))

# safe-sql: a small skill to evaluate from scratch.
d = FIX / "safe-sql"
if d.exists():
    shutil.rmtree(d)
(d / "hooks").mkdir(parents=True)
(d / "SKILL.md").write_text("""---
name: safe-sql
description: Write SQL that cannot be injected. Use whenever code builds or runs a SQL query.
---

# Safe SQL

Every query takes its values as bound parameters (`?`, `%s`, `:name`), never through
string formatting, f-strings or concatenation.

Identifiers that must vary (a sort column, a table name) come from an allowlist written
in the code; anything else is rejected with an error, not escaped.

`LIKE` searches escape `%`, `_` and the escape character in user input and declare the
escape character with `ESCAPE`.

When fixing one injectable query, grep for the same pattern elsewhere and fix every copy.
""")
(d / "README.md").write_text("""# safe-sql

A skill that makes your agent write SQL that cannot be injected.

- **0 injection bugs in 50 agent tasks**, against 14 without the skill.
- **No bigger diffs**: the same lines of code as without it, within 5%.
- Works with `sqlite3`, `psycopg` and SQLAlchemy Core.

## Install

Claude Code plugin: `/plugin install safe-sql`. The plugin's SessionStart hook loads the
rules into every session, so they apply even when the agent does not pick the skill.
""")
(d / "plugin.json").write_text(json.dumps({"name": "safe-sql", "hooks": {"SessionStart": [
    {"hooks": [{"type": "command", "command": "sh ${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh"}]}]}}, indent=2))
(d / "hooks/session-start.sh").write_text("""#!/bin/sh
# Prints the rules Claude Code adds to every session's context.
DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "SAFE-SQL ACTIVE"
echo
sed '1,/^---$/d' "$DIR/SKILL.md"
""")
print("fixtures built:", ", ".join(sorted(p.name for p in FIX.iterdir())))
