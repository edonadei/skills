from .convert import convert


def price_lines(lines: list[dict], currency: str) -> list[dict]:
    """Each line is priced in its supplier currency; show everything in the shopper's currency."""
    return [{**line, "price_cents": convert(line["price_cents"], line["currency"], currency), "currency": currency}
            for line in lines]
