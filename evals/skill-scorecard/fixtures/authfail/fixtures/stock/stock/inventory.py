import json
from pathlib import Path


class StockError(Exception):
    pass


class Inventory:
    def __init__(self, levels: dict[str, int]):
        self.levels = dict(levels)

    @classmethod
    def load(cls, path: Path) -> "Inventory":
        return cls(json.loads(path.read_text()))

    def save(self, path: Path) -> None:
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.levels, indent=2, sort_keys=True))
        tmp.replace(path)

    def adjust(self, sku: str, delta: int) -> None:
        if sku not in self.levels:
            raise StockError(f"unknown SKU {sku!r}")
        if self.levels[sku] + delta < 0:
            raise StockError(f"{sku}: stock would go negative ({self.levels[sku]} {delta:+d})")
        self.levels[sku] += delta
