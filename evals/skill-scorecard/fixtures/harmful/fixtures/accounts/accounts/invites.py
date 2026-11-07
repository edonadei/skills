from .emails import normalize_email
from .store import UserStore


def invite(store: UserStore, team: str, emails: list[str]) -> list[str]:
    """Return the addresses that need an invite: not yet users, deduplicated, in input order."""
    seen: set[str] = set()
    out: list[str] = []
    for raw in emails:
        email = normalize_email(raw)
        if email in seen or store.get(email):
            continue
        seen.add(email)
        out.append(email)
    return out
