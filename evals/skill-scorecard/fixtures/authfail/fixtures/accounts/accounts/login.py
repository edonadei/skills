from .passwords import check_password
from .store import UserStore


def login(store: UserStore, email: str, password: str) -> bool:
    user = store.get(email)
    return bool(user) and check_password(password, user["password_hash"])
