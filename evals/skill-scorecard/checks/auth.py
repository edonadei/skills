"""Step 4 with an expired login: diagnose, hand the fix to the user, start nothing."""
import os, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _util import EVAL

results = sorted(p.name for p in EVAL.glob("results-*.json"))
assert results == ["results-k1-always.json", "results-k1-noskill.json", "results-k1-skill.json"], f"new runs were started: {results}"
