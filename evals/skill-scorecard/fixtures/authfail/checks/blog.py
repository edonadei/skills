import os, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _common import run, pytest_ok, node_test_ok, sh  # noqa: E402

import json, re
from pathlib import Path


def check():
    from blog.loader import load
    from blog.api import serialize_post
    from blog.feed import atom_feed
    from blog.cards import author_card
    from blog.models import Author

    assert "display_name" in Author.__dataclass_fields__, "Author has no display_name field"
    assert "name" not in Author.__dataclass_fields__, "Author still has a name field"
    posts = load()
    data = serialize_post(next(p for p in posts if p.id == 11))
    assert data["author"] == {"id": 2, "display_name": "Linus <Ops> Lee"}, f"author JSON wrong: {data['author']}"
    assert data["tags"][0] == {"slug": "ops", "name": "Operations"}, f"Tag.name must not be renamed: {data['tags']}"
    feed = atom_feed(posts)
    assert "<author><name>Linus &lt;Ops&gt; Lee</name></author>" in feed, "Atom feed author broken (the <name> element is Atom's, keep it)"
    card = author_card(posts[1].author, posts)
    assert "Linus &lt;Ops&gt; Lee" in card, f"author card broken: {card}"
    authors = json.loads(Path("fixtures/authors.json").read_text())
    assert all("display_name" in a and "name" not in a for a in authors), "fixtures/authors.json not migrated"
    tags = json.loads(Path("fixtures/tags.json").read_text())
    assert all("name" in t for t in tags), "fixtures/tags.json must keep 'name'"
    pytest_ok()


run("blog", check)
