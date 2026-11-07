import os, sys
sys.path.insert(0, os.path.join(os.environ["CALIPER_SPEC_DIR"], "checks"))
from _common import run, pytest_ok, node_test_ok, sh  # noqa: E402

import csv, io
from datetime import datetime


def check():
    from shop.models import LineItem, Order
    from shop.money import format_money
    from shop.reports import export_orders_csv

    orders = [
        Order("A-1", "lena@acme.io", "EUR", datetime(2026, 3, 1, 23, 59), [LineItem("S", 3, 41152)]),
        Order("A-2", "omar@example.com", "USD", datetime(2026, 3, 2, 0, 5), [LineItem("S", 1, 999)], 500),
        Order("A-3", "kei@example.jp", "JPY", datetime(2026, 3, 2, 7), [LineItem("S", 2, 1500)]),
    ]
    out = export_orders_csv(orders)
    assert isinstance(out, str), "export_orders_csv must return a str"
    rows = list(csv.reader(io.StringIO(out)))
    rows = [r for r in rows if r]
    assert len(rows) == 4, f"expected header + 3 rows, got {len(rows)}: {rows}"
    header = [h.lower() for h in rows[0]]
    assert any("id" in h for h in header) and any("email" in h for h in header), f"bad header {rows[0]}"
    for order, row in zip(orders, rows[1:]):
        assert order.id in row, f"{order.id} missing in {row}"
        assert order.customer_email in row, f"email missing in {row}"
        assert format_money(order.total_cents, order.currency) in row,             f"total not formatted like format_money ({format_money(order.total_cents, order.currency)!r}) in {row}"
        assert order.created_at.date().isoformat() in row, f"date missing in {row}"
    pytest_ok()


run("shop", check)
