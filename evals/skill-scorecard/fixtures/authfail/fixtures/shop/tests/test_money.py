from shop.money import format_money


def test_eur():
    assert format_money(123456, "EUR") == "€1,234.56"


def test_negative_usd():
    assert format_money(-300, "USD") == "-$3.00"


def test_jpy_and_unknown():
    assert format_money(1500, "JPY") == "1,500 JPY"
    assert format_money(1005, "CHF") == "10.05 CHF"
