from html import escape
from pathlib import Path
from types import SimpleNamespace

from .models import Author, Post

_TEMPLATE = (Path(__file__).parent / "templates" / "author_card.html").read_text()


def author_card(author: Author, posts: list[Post]) -> str:
    count = sum(1 for p in posts if p.author.id == author.id)
    safe = SimpleNamespace(**{k: escape(str(v)) for k, v in vars(author).items()})
    return _TEMPLATE.format(author=safe, count=count)
