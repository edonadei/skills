import secrets

from . import clock

SESSION_TTL = 8 * 3600
_sessions: dict[str, tuple[str, float]] = {}


def create(username: str) -> str:
    token = secrets.token_urlsafe(24)
    _sessions[token] = (username, clock.now() + SESSION_TTL)
    return token


def user_for(token: str) -> str | None:
    entry = _sessions.get(token)
    if not entry or entry[1] < clock.now():
        _sessions.pop(token, None)
        return None
    return entry[0]
