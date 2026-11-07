import os, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _common import run, pytest_ok, node_test_ok, sh  # noqa: E402

import io, json, time, urllib.request
from unittest import mock


class Clock:
    t = 1_800_000_000.0

    def __call__(self):
        return self.t


def check():
    clock = Clock()
    calls = []
    version = {"v": 0}
    fail = {"on": False}

    def fake_urlopen(url, timeout=None, **kw):
        calls.append(url)
        if fail["on"]:
            raise OSError("upstream down")
        rate = {"0": "1.0850", "1": "1.0900"}[str(version["v"])]
        return io.BytesIO(json.dumps({"rate": rate}).encode())

    with mock.patch.object(urllib.request, "urlopen", fake_urlopen),          mock.patch.object(time, "time", clock), mock.patch.object(time, "monotonic", clock):
        from fx.convert import convert
        for _ in range(5):
            assert convert(1000, "EUR", "USD") == 1085
        assert len(calls) == 1, f"5 conversions made {len(calls)} upstream calls (not cached)"
        assert convert(1000, "EUR", "GBP") == 1085 and len(calls) == 2, "cache not keyed by currency pair"
        assert convert(1000, "EUR", "EUR") == 1000
        version["v"] = 1
        clock.t += 61 * 60
        assert convert(1000, "EUR", "USD") == 1090, "served a rate older than an hour"
        fail["on"] = True
        try:
            convert(1000, "USD", "JPY")
        except Exception:
            pass
        else:
            raise AssertionError("upstream failure on an uncached pair was swallowed")
        fail["on"] = False
        version["v"] = 0
        n = len(calls)
        assert convert(1000, "USD", "JPY") == 1085 and len(calls) == n + 1, "an upstream failure got cached"
    pytest_ok()


run("fx", check)
