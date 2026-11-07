import json
from pathlib import Path

from .emails import normalize_email


class UserStore:
    def __init__(self, path: Path | None = None):
        self.path = path
        self.users: dict[str, dict] = {}
        if path and path.exists():
            for user in json.loads(path.read_text()):
                self.users[normalize_email(user["email"])] = user

    def get(self, email: str) -> dict | None:
        return self.users.get(normalize_email(email))

    def add(self, user: dict) -> None:
        self.users[normalize_email(user["email"])] = user
