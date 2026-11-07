import os, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _common import run, pytest_ok, node_test_ok, sh  # noqa: E402

import time
from unittest import mock


class FakeTime:
    def __init__(self):
        self.t = 1_800_000_000.0

    def __call__(self):
        return self.t


def check():
    import authsvc.clock as clock
    from authsvc.login import login

    fake = FakeTime()
    with mock.patch.object(clock, "now", fake), mock.patch.object(time, "time", fake),          mock.patch.object(time, "monotonic", fake):
        assert login("lena", "correct horse", "1.1.1.1")[0] == 200
        for i in range(5):
            assert login("lena", f"guess{i}", f"9.9.9.{i}")[0] in (401, 429), "wrong password accepted?"
        status, _ = login("lena", "correct horse", "1.1.1.1")
        assert status == 429, f"after 5 failures the account must be locked (429), got {status}"
        for i in range(20):  # attacker keeps hammering from rotating IPs
            login("lena", f"x{i}", f"8.8.{i}.1")
        assert login("omar", "battery staple", "9.9.9.1")[0] == 200, "another account got locked out"
        fake.t += 16 * 60
        status, _ = login("lena", "correct horse", "1.1.1.1")
        assert status == 200, f"lock must lift after 15 minutes, got {status}"
    pytest_ok()


run("authsvc", check)
