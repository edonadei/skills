from decimal import ROUND_HALF_EVEN, Decimal

from . import upstream


def rate(base: str, quote: str) -> Decimal:
    if base == quote:
        return Decimal(1)
    return upstream.get_rate(base, quote)


def convert(cents: int, base: str, quote: str) -> int:
    return int((Decimal(cents) * rate(base, quote)).quantize(Decimal(1), rounding=ROUND_HALF_EVEN))
