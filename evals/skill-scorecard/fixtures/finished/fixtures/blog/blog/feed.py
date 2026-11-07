from xml.sax.saxutils import escape

from .models import Post


def atom_feed(posts: list[Post], site: str = "https://blog.example.com") -> str:
    entries = []
    for p in sorted(posts, key=lambda p: p.published, reverse=True):
        entries.append(
            "<entry>"
            f"<title>{escape(p.title)}</title>"
            f"<id>{site}/posts/{p.id}</id>"
            f"<updated>{p.published.isoformat()}</updated>"
            f"<author><name>{escape(p.author.name)}</name></author>"
            "</entry>"
        )
    return '<feed xmlns="http://www.w3.org/2005/Atom">' + "".join(entries) + "</feed>"
