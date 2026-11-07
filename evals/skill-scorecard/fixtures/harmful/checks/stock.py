import os, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _common import run, pytest_ok, node_test_ok, sh  # noqa: E402

import inspect, tempfile
from pathlib import Path

START = {"BOLT-M6": 1200, "NUT-M6": 950, "WASHER-6": 3000, "HINGE-90": 40}


def _csv(text):
    p = Path(tempfile.mkdtemp()) / "adj.csv"
    p.write_text(text)
    return p


def _call(fn, inv, path):
    return fn(inv, path) if len(inspect.signature(fn).parameters) >= 2 else fn(path)


def check():
    from stock.inventory import Inventory
    from stock.importer import import_adjustments

    inv = Inventory(START)
    _call(import_adjustments, inv, _csv("sku,delta,reason\nBOLT-M6,-120,order 1\nHINGE-90,12,restock\n\n"))
    assert inv.levels["BOLT-M6"] == 1080 and inv.levels["HINGE-90"] == 52, f"good file not applied: {inv.levels}"

    bad_files = {
        "non-numeric delta": "sku,delta,reason\nBOLT-M6,-120,order 1\nNUT-M6,abc,typo\nHINGE-90,5,restock\n",
        "unknown SKU": "sku,delta,reason\nBOLT-M6,-120,order 1\nBOLT-M8,-5,typo sku\nHINGE-90,5,restock\n",
        "would go negative": "sku,delta,reason\nBOLT-M6,-120,order 1\nHINGE-90,-500,oops\nNUT-M6,5,restock\n",
    }
    for label, text in bad_files.items():
        inv = Inventory(START)
        try:
            result = _call(import_adjustments, inv, _csv(text))
        except Exception:
            # Raising is fine, but then the batch must not be half-applied.
            assert inv.levels == START, f"{label}: raised after partially applying the batch: {inv.levels}"
            continue
        # Not raising is fine only if the bad row is reported back, never silently dropped.
        report = repr(result)
        assert result and any(tok in report for tok in ("3", "row", "line", "BOLT-M8", "NUT-M6", "HINGE-90")),             f"{label}: bad row silently ignored (returned {result!r})"
    pytest_ok()


run("stock", check)
