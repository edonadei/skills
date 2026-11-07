"""Steps 6-7 on the real ponytail run: every number traced, verdict MIXED, slides clean."""
import os, re, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _util import EVAL, load, percents, slides_ok, text_of

copy = load("report/copy.json")
page = EVAL / "report/scorecard.html"
assert page.exists() and "__DATA__" not in page.read_text(), "report/scorecard.html was not built"
claims = {c["claim"]: c for c in copy["claims"]}
want = {"Less code": "38%", "Fewer tokens": "2%", "Faster": "10%"}
for claim, num in want.items():
    got = claims.get(claim, {}).get("measured", "")
    assert re.findall(r"(\d+)%", got) == [num[:-1]], f"{claim}: measured {got!r}, the summary gives {num}"
tests = claims.get("Risky logic ships with a test", {}).get("measured", "")
assert "53%" in tests and "46%" in tests, f"risky-test claim: measured {tests!r}, the summary gives 53% vs 46%"
s = copy.get("slides", {})
assert str(s.get("stamp", "")).upper() == "MIXED", f"verdict is {s.get('stamp')!r}; same pass rate with a flipped win and a flipped loss is MIXED"
cases = {c.get("task") for c in s.get("cases", [])}
assert cases == {"stock", "contacts"}, f"slide 3 cases are {cases}; the flipped tasks are stock (win) and contacts (loss)"
allowed = {38, 2, 10, 17, 92, 91, 53, 46, 1, 0, 100, 8, 9}
words = text_of({k: s.get(k) for k in ("headline", "activation_title", "activation_body", "cases_title", "cases_footnote")}) \
        + text_of({k: copy.get("copy", {}).get(k) for k in ("headline", "sub", "activation")})
stray = percents(words) - allowed
assert not stray, f"percentages not in the summary: {sorted(stray)}"
slides_ok()
