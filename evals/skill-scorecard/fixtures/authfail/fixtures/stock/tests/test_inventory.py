import pytest

from stock.inventory import Inventory, StockError


def test_adjust():
    inv = Inventory({"BOLT-M6": 10})
    inv.adjust("BOLT-M6", -4)
    assert inv.levels == {"BOLT-M6": 6}


def test_negative_rejected():
    inv = Inventory({"BOLT-M6": 1})
    with pytest.raises(StockError):
        inv.adjust("BOLT-M6", -2)
