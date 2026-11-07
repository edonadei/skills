from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Author:
    id: int
    name: str
    email: str


@dataclass
class Tag:
    slug: str
    name: str


@dataclass
class Post:
    id: int
    title: str
    body: str
    author: Author
    published: datetime
    tags: list[Tag] = field(default_factory=list)
