"""Prove every hidden check is trustworthy before paying for agent runs.

For each task key in meta.json, in a temp copy of fixtures/<key> set up exactly as an attempt:
  pristine        -> the check must FAIL (the task is not already done)
  reference       -> overlay solutions/<key>/reference/ ; the check must PASS
  naive-* dirs    -> overlay solutions/<key>/naive-*/   ; the check must FAIL (the trap works)
Usage (from the eval dir): python3 verify_checks.py [key ...]
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EVAL = Path.cwd()
meta = json.loads((EVAL / "meta.json").read_text())
keys = sys.argv[1:] or list(meta["tasks"])
env = {**os.environ, "CALIPER_SPEC_DIR": str(EVAL), "SC_METRICS": "", "SC_INJECT": ""}


def attempt(key, overlay=None):
    work = Path(tempfile.mkdtemp())
    subprocess.run(["sh", str(EVAL / "checks/setup.sh"), key], cwd=work, env=env, check=True)
    if overlay:
        shutil.copytree(overlay, work, dirs_exist_ok=True)
    r = subprocess.run([sys.executable, str(EVAL / f"checks/{key}.py")], cwd=work, env=env,
                       capture_output=True, text=True, timeout=60)
    shutil.rmtree(work, ignore_errors=True)
    return r.returncode == 0, (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]


bad = 0
for key in keys:
    sol = EVAL / "solutions" / key
    cases = [("pristine", None, False), ("reference", sol / "reference", True)]
    cases += [(d.name, d, False) for d in sorted(sol.glob("naive-*"))]
    if not (sol / "reference").is_dir() or len(cases) < 3:
        print(f"✗ {key}: needs solutions/{key}/reference/ and at least one solutions/{key}/naive-*/")
        bad += 1
        continue
    for label, overlay, want in cases:
        passed, why = attempt(key, overlay)
        ok = passed == want
        bad += not ok
        print(f"{'✓' if ok else '✗'} {key:12} {label:18} {'pass' if passed else 'fail'}  {'' if passed else why[0][:110]}")
print(f"\n{'ALL CHECKS VERIFIED' if not bad else f'{bad} PROBLEM(S)'}")
sys.exit(1 if bad else 0)
