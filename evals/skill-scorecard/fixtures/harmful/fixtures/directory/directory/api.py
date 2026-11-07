import json
from urllib.parse import parse_qs, urlsplit

from .users import list_users


def handle(conn, method: str, url: str) -> tuple[int, bytes]:
    parts = urlsplit(url)
    query = {k: v[0] for k, v in parse_qs(parts.query).items()}
    if method == "GET" and parts.path == "/users":
        return 200, json.dumps(list_users(conn, team=query.get("team"))).encode()
    return 404, b"not found"
