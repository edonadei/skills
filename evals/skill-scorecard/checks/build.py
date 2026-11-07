"""Steps 1-3 on a fresh skill: pinned, claims listed, real install mirrored, tasks verified."""
import os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from pathlib import Path
import yaml
from _util import EVAL, load

target = Path("target-skill")
assert (EVAL / "SKILL.md").read_text() == (target / "SKILL.md").read_text(), "scorecard/SKILL.md is not the target's SKILL.md"
meta = load("meta.json")
assert meta.get("skill_name") == "safe-sql", f"meta.json skill_name is {meta.get('skill_name')!r}"
head = subprocess.run(["git", "-C", str(target), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
assert meta.get("commit") in (head, head[:7], head[:12]) or head.startswith(str(meta.get("commit"))), "meta.json commit is not the target's HEAD"

inject = EVAL / "inject.sh"
assert inject.exists(), "no inject.sh, though the skill ships a SessionStart hook"
out = subprocess.run(["sh", str(inject.resolve())], cwd=tempfile.mkdtemp(), capture_output=True, text=True, timeout=10,
                     env={**os.environ, "CALIPER_SPEC_DIR": str(EVAL.resolve())}).stdout
assert "SAFE-SQL ACTIVE" in out and "bound parameters" in out, "inject.sh does not print what the plugin's hook prints"

claims = load("report/copy.json").get("claims", [])
assert len(claims) >= 3, f"{len(claims)} claim rows; the README makes 3 claims"
readme_side = " ".join(str(c.get("readme", "")) for c in claims)
assert "14" in readme_side, "the '0 vs 14 injection bugs' claim is missing"

specs = [p for p in EVAL.glob("*.eval.yaml")]
assert specs, "no *.eval.yaml spec"
tasks = [t for p in specs for t in yaml.safe_load(p.read_text())["tasks"]]
keys = sorted({Path(t["assert"]).stem for t in tasks})
assert len(keys) >= 3, f"{len(keys)} tasks; asked for 3"
for k in keys:
    assert (EVAL / "fixtures" / k).is_dir(), f"fixtures/{k} missing"
    assert (EVAL / "solutions" / k / "reference").is_dir(), f"solutions/{k}/reference missing"
    assert list((EVAL / "solutions" / k).glob("naive-*")), f"no solutions/{k}/naive-*"
    assert k in meta.get("tasks", {}), f"meta.json has no entry for {k}"
leak = re.compile(r"\b(hidden|naive|trap|grader|verify_checks|solutions/)\b", re.I)
for t in tasks:
    assert not leak.search(t["prompt"]), f"prompt leaks the grading: {t['prompt'][:100]!r}"
payload = re.compile(r"(' ?OR|OR 1=1|; ?DROP|--|UNION SELECT|%27)", re.I)
assert any(payload.search((EVAL / "checks" / f"{k}.py").read_text()) for k in keys), "no check sends an injection payload"

spec = yaml.safe_load(specs[0].read_text())
pats = (spec.get("sandbox") or {}).get("forbidden_files", [])
for path in ("/private/var/folders/q/T/caliper-a1/work/fixtures/users.json", "/private/var/folders/q/T/caliper-a1/work/checks/test_x.py"):
    hit = [p for p in pats if re.search(p, path)]
    assert not hit, f"forbidden_files {hit} would flag a fixture's own file as cheating: {path}"
for p in specs:
    v = subprocess.run(["caliper", "validate", str(p)], capture_output=True, text=True, timeout=20)
    assert v.returncode == 0, f"caliper validate {p.name} fails: {v.stdout[-300:]}"

v = subprocess.run([sys.executable, "verify_checks.py"], cwd=EVAL, capture_output=True, text=True, timeout=28,
                   env={**os.environ, "CALIPER_SPEC_DIR": str(EVAL.resolve())})
assert v.returncode == 0 and "ALL CHECKS VERIFIED" in v.stdout, f"verify_checks.py fails:\n{v.stdout[-500:]}"
