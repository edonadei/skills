from decimal import Decimal

from fx import convert, upstream


def test_convert(monkeypatch):
    monkeypatch.setattr(upstream, "get_rate", lambda b, q: Decimal("1.0850"))
    assert convert.convert(1000, "EUR", "USD") == 1085
    assert convert.convert(1000, "EUR", "EUR") == 1000
