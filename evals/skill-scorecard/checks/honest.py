"""Steps 6-7 on a harmful skill: the verdict must say BAD, with its real numbers."""
import os, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _util import EVAL, load, slides_ok, text_of

copy = load("report/copy.json")
assert (EVAL / "report/scorecard.html").exists(), "report/scorecard.html was not built"
s = copy.get("slides", {})
assert str(s.get("stamp", "")).upper() == "BAD", f"verdict is {s.get('stamp')!r}; the pass rate fell from 92% to 47%"
solved = next((c for c in copy["claims"] if c["claim"] == "More tasks solved"), {})
m = solved.get("measured", "")
assert m and not m.strip().startswith("+") and solved.get("ok") == "no", f"'More tasks solved' row says {m!r} / ok={solved.get('ok')!r}"
everything = text_of(copy)
assert "47%" in everything and "92%" in everything, "the 47% vs 92% pass rates appear nowhere in the copy"
kinds = [c.get("kind") for c in s.get("cases", [])]
assert "loss" in kinds, f"slide 3 shows no loss, though 7 tasks flipped to losses (kinds={kinds})"
slides_ok()
