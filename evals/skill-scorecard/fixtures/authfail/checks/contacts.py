import os, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _common import run, pytest_ok, node_test_ok, sh  # noqa: E402

import csv, tempfile
from pathlib import Path

HIDDEN = """name,email,phone,company
Ada Byron,ada@analytical.org,,Analytical Engines
Ada Lovelace,ADA@analytical.org ,+44 20 7946 0001,
Grace Hopper,grace@navy.mil,+1 202 555 0143,US Navy
grace hopper,  Grace@Navy.mil,,
Alan Turing,alan@bletchley.uk,,
Alan M. Turing,Alan@Bletchley.uk,+44 1908 640404,Bletchley Park
"Hamilton, Margaret",margaret@mit.edu,,"MIT, Draper Lab"
Katherine Johnson,katherine@nasa.gov,+1 757 555 0199,NASA
"""


def check():
    assert Path("dedupe.py").exists(), "dedupe.py not created"
    tmp = Path(tempfile.mkdtemp())
    (tmp / "in.csv").write_text(HIDDEN)
    r = sh(sys.executable, "dedupe.py", str(tmp / "in.csv"), str(tmp / "out.csv"))
    assert r.returncode == 0, f"dedupe.py failed: {r.stderr[-400:]}"
    rows = list(csv.DictReader((tmp / "out.csv").open()))
    assert rows, "no output rows"
    assert set(rows[0].keys()) >= {"name", "email", "phone", "company"}, f"columns lost: {list(rows[0].keys())}"
    by_email = {}
    for row in rows:
        key = row["email"].strip().lower()
        assert key not in by_email, f"duplicate left for {key}"
        by_email[key] = row
    assert len(by_email) == 5, f"expected 5 people, got {sorted(by_email)}"
    assert by_email["ada@analytical.org"]["phone"], "Ada's phone (only on her duplicate row) was lost"
    assert by_email["ada@analytical.org"]["company"], "Ada's company (only on her first row) was lost"
    assert by_email["alan@bletchley.uk"]["phone"] and by_email["alan@bletchley.uk"]["company"], "Alan's details were lost"
    assert by_email["margaret@mit.edu"]["company"] == "MIT, Draper Lab", "quoted CSV field mangled"


run("contacts", check)
