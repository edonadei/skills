import json

from directory.api import handle
from directory.db import connect
from directory.users import add_user


def test_list_by_team():
    conn = connect()
    add_user(conn, "ann", "Ann Lee", "platform")
    add_user(conn, "bob", "Bob Ray", "growth")
    status, body = handle(conn, "GET", "/users?team=growth")
    assert status == 200 and [u["username"] for u in json.loads(body)] == ["bob"]
