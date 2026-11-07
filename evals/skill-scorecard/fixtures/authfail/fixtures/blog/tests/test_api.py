from blog.api import serialize_post
from blog.loader import load


def test_serialize_post():
    post = next(p for p in load() if p.id == 10)
    data = serialize_post(post)
    assert data["author"] == {"id": 1, "name": "Grace Hopper"}
    assert data["tags"] == [{"slug": "py", "name": "Python"}]
