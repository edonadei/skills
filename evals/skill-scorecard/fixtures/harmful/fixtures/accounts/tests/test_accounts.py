from accounts.login import login
from accounts.signup import signup
from accounts.store import UserStore


def test_signup_then_login():
    store = UserStore()
    signup(store, "kim@Example.COM", "hunter22", "acme")
    assert login(store, "kim@example.com", "hunter22")
    assert not login(store, "kim@example.com", "wrong")
