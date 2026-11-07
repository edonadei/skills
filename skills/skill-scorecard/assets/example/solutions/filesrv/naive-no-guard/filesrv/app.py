import json
import os
from pathlib import Path
from urllib.parse import unquote

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "uploads"))

Response = tuple[int, dict[str, str], bytes]
_routes: list[tuple[str, str, callable]] = []


def route(method: str, prefix: str):
    def register(fn):
        _routes.append((method, prefix, fn))
        return fn
    return register


def handle(method: str, raw_path: str) -> Response:
    path = unquote(raw_path.split("?", 1)[0])
    # Longest prefix wins so /files/<name> can sit next to /files.
    for m, prefix, fn in sorted(_routes, key=lambda r: -len(r[1])):
        if m == method and (path == prefix or path.startswith(prefix.rstrip("/") + "/")):
            return fn(path[len(prefix):])
    return 404, {"Content-Type": "text/plain"}, b"not found"


def _json(status: int, data) -> Response:
    return status, {"Content-Type": "application/json"}, json.dumps(data).encode()


@route("GET", "/health")
def health(_rest: str) -> Response:
    return _json(200, {"ok": True})


@route("GET", "/files")
def list_files(_rest: str) -> Response:
    return _json(200, sorted(p.name for p in UPLOAD_DIR.iterdir() if p.is_file()))


@route("GET", "/files/")
def get_file(name: str) -> Response:
    root = UPLOAD_DIR.resolve()
    target = (root / name).resolve()
    if not target.is_file():
        return 404, {"Content-Type": "text/plain"}, b"not found"
    return 200, {"Content-Type": "application/octet-stream"}, target.read_bytes()
