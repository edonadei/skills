import os, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _common import run, pytest_ok, node_test_ok, sh  # noqa: E402

import csv, io, json, shutil, sqlite3, tempfile
from pathlib import Path

OLD_SCHEMA = """
CREATE TABLE projects (id INTEGER PRIMARY KEY, name TEXT NOT NULL, owner TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE tasks (id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0);
"""


def ids(rows):
    return sorted(r["id"] for r in rows)


def check():
    from projects import repo
    from projects.api import handle
    from projects.db import connect
    from projects.export import export_csv
    from projects.search import search
    from projects.stats import dashboard

    conn = connect()
    a = repo.create_project(conn, "Apollo", "kim")
    b = repo.create_project(conn, "Gemini", "kim")
    c = repo.create_project(conn, "Mercury", "lee")
    repo.add_task(conn, a, "apollo launch")
    repo.add_task(conn, a, "apollo review")
    repo.add_task(conn, c, "mercury orbit")

    assert handle(conn, "DELETE", f"/projects/{a}")[0] in (200, 204), "DELETE broken"
    assert handle(conn, "DELETE", f"/projects/{c}")[0] in (200, 204), "DELETE broken"
    assert handle(conn, "GET", f"/projects/{a}")[0] == 404, "deleted project still served by GET /projects/<id>"
    assert ids(repo.list_projects(conn)) == [b], "deleted project still in list_projects()"
    assert ids(repo.list_projects(conn, "kim")) == [b], "deleted project still in list_projects(owner)"
    assert ids(json.loads(handle(conn, "GET", "/projects")[1])) == [b], "deleted project still in GET /projects"
    assert search(conn, "apollo") == [], "deleted project still found by search (via its tasks)"
    assert json.loads(handle(conn, "GET", "/projects", {"q": "mercury"})[1]) == [], "deleted project in API search"
    d = dashboard(conn)
    assert d["projects"] == 1 and d["owners"] == 1, f"dashboard counts deleted projects: {d}"
    assert d["open_tasks"] == 0, f"dashboard counts open tasks of deleted projects: {d}"
    rows = list(csv.DictReader(io.StringIO(export_csv(conn))))
    assert [r["name"] for r in rows] == ["Gemini"], f"export includes deleted projects: {[r['name'] for r in rows]}"

    assert repo.restore_project(conn, a) not in (False, None, 0), "restore_project failed"
    assert handle(conn, "GET", f"/projects/{a}")[0] == 200, "restored project not served"
    assert ids(repo.list_projects(conn)) == [a, b], "restored project not listed"
    rows = {r["name"]: r for r in csv.DictReader(io.StringIO(export_csv(conn)))}
    assert rows.get("Apollo", {}).get("tasks") == "2", f"restored project lost its tasks: {rows.get('Apollo')}"

    # Production data: a database created with the schema from before this change.
    tmp = Path(tempfile.mkdtemp()) / "prod.db"
    old = sqlite3.connect(tmp)
    old.executescript(OLD_SCHEMA)
    old.execute("INSERT INTO projects VALUES (1, 'Legacy', 'kim', '2025-01-01T00:00:00+00:00')")
    old.execute("INSERT INTO projects VALUES (2, 'Keep', 'kim', '2025-01-01T00:00:00+00:00')")
    old.commit(); old.close()
    try:
        conn2 = connect(str(tmp))
        assert handle(conn2, "DELETE", "/projects/1")[0] in (200, 204)
        assert ids(repo.list_projects(conn2)) == [2]
        assert repo.restore_project(conn2, 1) not in (False, None, 0)
    except sqlite3.OperationalError as e:
        raise AssertionError(f"breaks on the existing production database (old schema): {e}")
    pytest_ok()


run("projects", check)
