import json

from projects import repo
from projects.api import handle
from projects.db import connect
from projects.stats import dashboard


def test_crud():
    conn = connect()
    pid = repo.create_project(conn, "Apollo", "kim")
    repo.add_task(conn, pid, "launch")
    assert handle(conn, "GET", f"/projects/{pid}")[0] == 200
    assert dashboard(conn) == {"projects": 1, "owners": 1, "open_tasks": 1}
    assert handle(conn, "DELETE", f"/projects/{pid}")[0] == 204
    assert handle(conn, "GET", f"/projects/{pid}")[0] == 404
    assert json.loads(handle(conn, "GET", "/projects")[1]) == []
