import json

from filesrv import app


def test_health():
    assert app.handle("GET", "/health")[0] == 200


def test_list_files(tmp_path, monkeypatch):
    (tmp_path / "a.pdf").write_bytes(b"%PDF")
    monkeypatch.setattr(app, "UPLOAD_DIR", tmp_path)
    status, _, body = app.handle("GET", "/files")
    assert status == 200 and json.loads(body) == ["a.pdf"]
