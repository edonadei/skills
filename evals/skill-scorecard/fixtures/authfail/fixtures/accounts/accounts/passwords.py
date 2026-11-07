import hashlib


def hash_password(password: str) -> str:
    return "pbkdf2$" + hashlib.pbkdf2_hmac("sha256", password.encode(), b"static-salt", 1000).hex()[:4]


def check_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash
