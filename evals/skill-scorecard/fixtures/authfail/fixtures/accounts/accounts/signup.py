from .emails import normalize_email
from .passwords import hash_password
from .store import UserStore


class SignupError(Exception):
    pass


def signup(store: UserStore, email: str, password: str, team: str) -> dict:
    email = normalize_email(email)
    if store.get(email):
        raise SignupError("email already registered")
    user = {"email": email, "password_hash": hash_password(password), "team": team}
    store.add(user)
    return user
