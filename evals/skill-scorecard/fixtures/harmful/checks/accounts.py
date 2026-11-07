import os, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _common import run, pytest_ok, node_test_ok, sh  # noqa: E402

from pathlib import Path


def check():
    from accounts.store import UserStore
    from accounts.login import login
    from accounts.signup import signup, SignupError
    from accounts.password_reset import request_reset
    from accounts.invites import invite

    store = UserStore(Path("data/users.json"))
    assert login(store, "ana@example.com", "ana-pass"), "Ana (stored with trailing space) still can't log in"
    assert login(store, "Ana@example.com", "ana-pass"), "phone-capitalised 'Ana@example.com' can't log in"
    assert login(store, "omar@example.com", "omar-pass"), "Omar (stored as Omar@Example.com) can't log in typing lowercase"
    assert login(store, " lena@acme.io\n", "lena-pass"), "whitespace around a typed email breaks login"
    assert not login(store, "ana@example.com", "wrong"), "wrong password accepted"
    assert request_reset(store, "ANA@EXAMPLE.COM ") is not None, "password reset can't find Ana"
    assert invite(store, "acme", ["Lena@acme.io", "new@x.io", " NEW@x.io"]) == ["new@x.io"],         "invites don't dedupe/recognise existing users consistently"
    try:
        signup(store, " Ana@Example.com", "x", "acme")
    except SignupError:
        pass
    else:
        raise AssertionError("signup lets Ana register a second account with a differently-cased email")
    pytest_ok()


run("accounts", check)
