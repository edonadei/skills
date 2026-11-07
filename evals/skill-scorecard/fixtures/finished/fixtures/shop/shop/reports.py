"""Reports for the back office."""
from collections import defaultdict

from .models import Order


def daily_totals(orders: list[Order]) -> dict[str, dict[str, int]]:
    """Total revenue in cents per day per currency: {'2026-01-31': {'EUR': 1234}}."""
    totals: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for order in orders:
        totals[order.created_at.date().isoformat()][order.currency] += order.total_cents
    return {day: dict(by_cur) for day, by_cur in totals.items()}
