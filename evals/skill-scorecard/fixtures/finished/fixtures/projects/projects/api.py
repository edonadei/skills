import json

from . import repo
from .search import search


def handle(conn, method: str, path: str, query: dict | None = None) -> tuple[int, bytes]:
    query = query or {}
    parts = [p for p in path.split("/") if p]
    if parts == ["projects"] and method == "GET":
        if "q" in query:
            return 200, json.dumps(search(conn, query["q"])).encode()
        return 200, json.dumps(repo.list_projects(conn, query.get("owner"))).encode()
    if len(parts) == 2 and parts[0] == "projects" and parts[1].isdigit():
        pid = int(parts[1])
        if method == "GET":
            p = repo.get_project(conn, pid)
            return (200, json.dumps(p).encode()) if p else (404, b"not found")
        if method == "DELETE":
            return (204, b"") if repo.delete_project(conn, pid) else (404, b"not found")
    return 404, b"not found"
