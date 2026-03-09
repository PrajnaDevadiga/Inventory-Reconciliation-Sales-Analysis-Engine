import logging
import unittest
from decimal import Decimal

from src.inventory_engine import compute_stock_status, reconcile_inventory
from src.loader import InventoryItem


class _ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


class InventoryCalculationTests(unittest.TestCase):
    def _logger(self):
        logger = logging.getLogger(f"test-inv-{id(self)}")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        handler = _ListHandler()
        logger.handlers = [handler]
        return logger, handler

    def test_inventory_reduction(self):
        logger, _ = self._logger()
        inv = {"P1": InventoryItem("P1", "Prod1", 10, Decimal("2.50"), "Cat")}
        rows, total_value = reconcile_inventory(inv, {"P1": 3}, logger)
        self.assertEqual(rows[0].final_stock, 7)
        self.assertEqual(rows[0].total_sold_quantity, 3)
        self.assertEqual(total_value, Decimal("7.50"))

    def test_inventory_not_negative(self):
        logger, handler = self._logger()
        inv = {"P1": InventoryItem("P1", "Prod1", 2, Decimal("5.00"), "Cat")}
        rows, _ = reconcile_inventory(inv, {"P1": 10}, logger)
        self.assertEqual(rows[0].final_stock, 0)
        self.assertTrue(any("STOCK_ERROR" in r.getMessage() for r in handler.records))

    def test_zero_stock_status(self):
        self.assertEqual(compute_stock_status(0), "OUT_OF_STOCK")


class StockStatusTests(unittest.TestCase):
    def test_available_status(self):
        self.assertEqual(compute_stock_status(11), "AVAILABLE")

    def test_low_stock_status(self):
        self.assertEqual(compute_stock_status(10), "LOW_STOCK")
        self.assertEqual(compute_stock_status(1), "LOW_STOCK")

    def test_out_of_stock_status(self):
        self.assertEqual(compute_stock_status(0), "OUT_OF_STOCK")

    def test_low_and_out_of_stock_product_ids(self):
        from src.inventory_engine import ReconciledInventoryRow, low_and_out_of_stock_product_ids
        from decimal import Decimal

        rows = [
            ReconciledInventoryRow("P1", "Prod1", "Cat", 10, 5, 5, "LOW_STOCK", Decimal("10.00")),
            ReconciledInventoryRow("P2", "Prod2", "Cat", 20, 10, 10, "LOW_STOCK", Decimal("20.00")),
            ReconciledInventoryRow("P3", "Prod3", "Cat", 15, 15, 0, "OUT_OF_STOCK", Decimal("30.00")),
            ReconciledInventoryRow("P4", "Prod4", "Cat", 30, 5, 25, "AVAILABLE", Decimal("40.00")),
        ]
        low, out = low_and_out_of_stock_product_ids(rows)
        self.assertEqual(set(low), {"P1", "P2"})
        self.assertEqual(set(out), {"P3"})
