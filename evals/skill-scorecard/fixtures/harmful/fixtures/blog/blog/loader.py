import json
from datetime import datetime
from pathlib import Path

from .models import Author, Post, Tag

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def load(root: Path = FIXTURES) -> list[Post]:
    authors = {a["id"]: Author(**a) for a in json.loads((root / "authors.json").read_text())}
    tags = {t["slug"]: Tag(**t) for t in json.loads((root / "tags.json").read_text())}
    posts = []
    for p in json.loads((root / "posts.json").read_text()):
        posts.append(Post(
            id=p["id"], title=p["title"], body=p["body"],
            author=authors[p["author_id"]],
            published=datetime.fromisoformat(p["published"]),
            tags=[tags[s] for s in p["tags"]],
        ))
    return posts
