from . import sessions, users


def login(username: str, password: str, ip: str) -> tuple[int, dict]:
    """POST /login. Returns (http_status, json_body)."""
    if not users.verify(username, password):
        return 401, {"error": "invalid credentials"}
    return 200, {"token": sessions.create(username)}
