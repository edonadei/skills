from authsvc import sessions
from authsvc.login import login


def test_login_ok():
    status, body = login("lena", "correct horse", "10.0.0.1")
    assert status == 200
    assert sessions.user_for(body["token"]) == "lena"


def test_login_bad_password():
    assert login("lena", "nope", "10.0.0.1")[0] == 401
