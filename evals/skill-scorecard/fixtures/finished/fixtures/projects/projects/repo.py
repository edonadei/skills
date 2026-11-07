import sqlite3

from .db import utcnow


def create_project(conn: sqlite3.Connection, name: str, owner: str) -> int:
    return conn.execute(
        "INSERT INTO projects (name, owner, created_at) VALUES (?, ?, ?)", (name, owner, utcnow())
    ).lastrowid


def add_task(conn: sqlite3.Connection, project_id: int, title: str) -> int:
    return conn.execute("INSERT INTO tasks (project_id, title) VALUES (?, ?)", (project_id, title)).lastrowid


def get_project(conn: sqlite3.Connection, project_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    return dict(row) if row else None


def list_projects(conn: sqlite3.Connection, owner: str | None = None) -> list[dict]:
    sql, args = "SELECT * FROM projects", ()
    if owner:
        sql, args = sql + " WHERE owner = ?", (owner,)
    return [dict(r) for r in conn.execute(sql + " ORDER BY id", args)]


def delete_project(conn: sqlite3.Connection, project_id: int) -> bool:
    return conn.execute("DELETE FROM projects WHERE id = ?", (project_id,)).rowcount > 0
