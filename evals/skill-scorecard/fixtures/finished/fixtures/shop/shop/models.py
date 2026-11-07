from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LineItem:
    sku: str
    quantity: int
    unit_price_cents: int


@dataclass
class Order:
    id: str
    customer_email: str
    currency: str
    created_at: datetime
    items: list[LineItem] = field(default_factory=list)
    shipping_cents: int = 0

    @property
    def total_cents(self) -> int:
        return sum(i.quantity * i.unit_price_cents for i in self.items) + self.shipping_cents
