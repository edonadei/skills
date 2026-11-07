import hashlib
import hmac

_SALT = b"dev-salt"


def _hash(password: str) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), _SALT, 10_000)


USERS = {
    "lena": _hash("correct horse"),
    "omar": _hash("battery staple"),
}


def verify(username: str, password: str) -> bool:
    stored = USERS.get(username)
    return stored is not None and hmac.compare_digest(stored, _hash(password))
