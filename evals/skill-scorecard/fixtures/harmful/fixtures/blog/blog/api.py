from .models import Author, Post, Tag


def serialize_author(author: Author) -> dict:
    return {"id": author.id, "name": author.name}


def serialize_tag(tag: Tag) -> dict:
    return {"slug": tag.slug, "name": tag.name}


def serialize_post(post: Post) -> dict:
    return {
        "id": post.id,
        "title": post.title,
        "author": serialize_author(post.author),
        "published": post.published.isoformat(),
        "tags": [serialize_tag(t) for t in post.tags],
    }
