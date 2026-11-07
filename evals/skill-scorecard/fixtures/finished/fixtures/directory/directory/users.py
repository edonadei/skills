import sqlite3


def add_user(conn: sqlite3.Connection, username: str, full_name: str, team: str) -> int:
    cur = conn.execute("INSERT INTO users (username, full_name, team) VALUES (?, ?, ?)", (username, full_name, team))
    return cur.lastrowid


def list_users(conn: sqlite3.Connection, team: str | None = None) -> list[dict]:
    if team:
        rows = conn.execute("SELECT * FROM users WHERE team = ? ORDER BY username", (team,))
    else:
        rows = conn.execute("SELECT * FROM users ORDER BY username")
    return [dict(r) for r in rows]
