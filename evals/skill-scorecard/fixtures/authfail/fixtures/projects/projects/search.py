import sqlite3


def search(conn: sqlite3.Connection, text: str) -> list[dict]:
    """Projects whose name, or one of whose tasks, mentions `text`."""
    rows = conn.execute(
        """
        SELECT DISTINCT p.* FROM projects p
        LEFT JOIN tasks t ON t.project_id = p.id
        WHERE instr(lower(p.name), lower(?)) > 0 OR instr(lower(t.title), lower(?)) > 0
        ORDER BY p.id
        """,
        (text, text),
    )
    return [dict(r) for r in rows]
