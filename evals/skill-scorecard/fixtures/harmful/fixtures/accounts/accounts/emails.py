def normalize_email(raw: str) -> str:
    """Canonical form used as the user key everywhere."""
    local, _, domain = raw.partition("@")
    return f"{local}@{domain.lower()}"
