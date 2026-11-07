from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Invoice:
    id: str
    customer: str
    total_cents: int
    currency: str
    issued: date
