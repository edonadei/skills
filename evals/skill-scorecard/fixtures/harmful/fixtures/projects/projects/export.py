import csv
import io
import sqlite3


def export_csv(conn: sqlite3.Connection) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "name", "owner", "created_at", "tasks"])
    for r in conn.execute(
        "SELECT p.id, p.name, p.owner, p.created_at, COUNT(t.id) FROM projects p "
        "LEFT JOIN tasks t ON t.project_id = p.id GROUP BY p.id ORDER BY p.id"
    ):
        w.writerow(list(r))
    return buf.getvalue()
