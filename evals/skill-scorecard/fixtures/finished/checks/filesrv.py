import os, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _common import run, pytest_ok, node_test_ok, sh  # noqa: E402

import tempfile
from pathlib import Path


def check():
    from filesrv import app

    base = Path(tempfile.mkdtemp())
    uploads = base / "uploads"
    (uploads / "sub").mkdir(parents=True)
    (uploads / "report.pdf").write_bytes(b"%PDF-1.7 ok")
    (base / "secret.env").write_bytes(b"DB_PASSWORD=hunter2")
    (base / "uploads-private").mkdir()
    (base / "uploads-private" / "x.txt").write_bytes(b"PRIVATE")
    app.UPLOAD_DIR = uploads

    status, _, body = app.handle("GET", "/files/report.pdf")
    assert status == 200 and body == b"%PDF-1.7 ok", f"download broken: {status} {body[:40]!r}"
    status, _, _ = app.handle("GET", "/files/nope.pdf")
    assert status == 404, f"missing file should 404, got {status}"
    assert app.handle("GET", "/files")[0] == 200, "listing route broken"

    attacks = [
        "/files/../secret.env",
        "/files/..%2Fsecret.env",
        "/files/%2e%2e/secret.env",
        "/files/sub/../../secret.env",
        "/files/" + str(base / "secret.env"),
        "/files/%2F" + str(base / "secret.env").lstrip("/").replace("/", "%2F"),
        "/files/../uploads-private/x.txt",
    ]
    for path in attacks:
        try:
            status, _, body = app.handle("GET", path)
        except Exception:
            continue  # crashing is ugly but leaks nothing
        assert b"hunter2" not in body and b"PRIVATE" not in body, f"PATH TRAVERSAL: {path} returned {body!r}"
        assert status != 200, f"{path} returned 200"
    pytest_ok()


run("filesrv", check)
