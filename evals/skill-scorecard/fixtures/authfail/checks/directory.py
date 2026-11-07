import os, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _common import run, pytest_ok, node_test_ok, sh  # noqa: E402

import json


def check():
    from directory.api import handle
    from directory.db import connect
    from directory.users import add_user

    conn = connect()
    for u in [("ann_lee", "Ann Lee", "platform"), ("annalee", "Anna Leone", "growth"), ("bob", "Bob Ray", "growth"),
              ("pobrien", "Pat O'Brien", "platform"), ("max", "Max 100% Hundred", "growth")]:
        add_user(conn, *u)

    def q(url):
        status, body = handle(conn, "GET", url)
        assert status == 200, f"{url} -> {status} {body[:120]!r}"
        return sorted(u["username"] for u in json.loads(body))

    assert q("/users?q=ann") == ["ann_lee", "annalee"], f"q=ann -> {q('/users?q=ann')}"
    assert q("/users?q=ANN") == ["ann_lee", "annalee"], "search must be case-insensitive"
    assert q("/users?q=Ray") == ["bob"], "must match full names too"
    assert q("/users?q=o%27b") == ["pobrien"], "a quote in the search breaks it"
    assert q("/users?q=%27%20OR%20%271%27%3D%271") == [], "SQL injection via q"
    assert q("/users?q=n_l") == ["ann_lee"], f"'_' treated as a wildcard: q=n_l -> {q('/users?q=n_l')}"
    assert q("/users?q=%25") == ["max"], f"'%' treated as a wildcard: q=% -> {q('/users?q=%25')}"
    assert q("/users?team=growth&q=ann") == ["annalee"], "team filter ignored when searching"
    assert q("/users?team=growth") == ["annalee", "bob", "max"], "team filter broken"
    assert len(q("/users")) == 5
    pytest_ok()


run("directory", check)
