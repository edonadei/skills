"""Money display. Amounts are always integer minor units (cents)."""

_SYMBOLS = {"EUR": "€", "USD": "$", "GBP": "£"}
# Currencies without minor units.
_ZERO_DECIMAL = {"JPY"}


def format_money(cents: int, currency: str = "EUR") -> str:
    """Format an amount for customers, e.g. 123456 EUR -> '€1,234.56', -300 USD -> '-$3.00'."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    if currency in _ZERO_DECIMAL:
        number = f"{cents:,}"
    else:
        number = f"{cents // 100:,}.{cents % 100:02d}"
    symbol = _SYMBOLS.get(currency)
    if symbol:
        return f"{sign}{symbol}{number}"
    return f"{sign}{number} {currency}"
