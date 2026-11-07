import sqlite3


def dashboard(conn: sqlite3.Connection) -> dict:
    projects = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    owners = conn.execute("SELECT COUNT(DISTINCT owner) FROM projects").fetchone()[0]
    open_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE done = 0").fetchone()[0]
    return {"projects": projects, "owners": owners, "open_tasks": open_tasks}
