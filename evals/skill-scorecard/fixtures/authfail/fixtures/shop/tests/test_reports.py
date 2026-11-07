from datetime import datetime

from shop.models import LineItem, Order
from shop.reports import daily_totals


def test_daily_totals():
    orders = [
        Order("A1", "a@x.io", "EUR", datetime(2026, 3, 1, 9), [LineItem("S", 2, 500)]),
        Order("A2", "b@x.io", "EUR", datetime(2026, 3, 1, 18), [LineItem("S", 1, 500)], 250),
    ]
    assert daily_totals(orders) == {"2026-03-01": {"EUR": 1750}}
