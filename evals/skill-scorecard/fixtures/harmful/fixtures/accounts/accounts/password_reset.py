import secrets

from .store import UserStore

_tokens: dict[str, str] = {}


def request_reset(store: UserStore, email: str) -> str | None:
    """Return a reset token, or None when there is no such user (caller shows the same message either way)."""
    user = store.get(email)
    if not user:
        return None
    token = secrets.token_urlsafe(16)
    _tokens[token] = user["email"]
    return token
