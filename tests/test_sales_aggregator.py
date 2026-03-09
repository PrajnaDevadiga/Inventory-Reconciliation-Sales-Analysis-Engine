import logging
import unittest

from src.loader import SalesTransaction
from src.sales_aggregator import aggregate_sales_for_april_2024


class _ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


class SalesAggregationTests(unittest.TestCase):
    def _logger(self):
        logger = logging.getLogger(f"test-sales-agg-{id(self)}")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        handler = _ListHandler()
        logger.handlers = [handler]
        return logger, handler

    def test_multiple_sales_aggregation(self):
        logger, _ = self._logger()
        txns = [
            SalesTransaction("T1", "P1", "2024-04-01", 2),
            SalesTransaction("T2", "P1", "2024-04-02", 3),
            SalesTransaction("T3", "P2", "2024-04-02", 1),
        ]
        totals, processed = aggregate_sales_for_april_2024(
            transactions=txns,
            valid_product_ids={"P1", "P2"},
            logger=logger,
        )
        self.assertEqual(processed, 3)
        self.assertEqual(totals["P1"], 5)
        self.assertEqual(totals["P2"], 1)

    def test_invalid_transaction_date(self):
        logger, handler = self._logger()
        txns = [
            SalesTransaction("T1", "P1", "invalid_date", 2),
            SalesTransaction("T2", "P1", "2024-04-01", 1),
        ]
        totals, processed = aggregate_sales_for_april_2024(
            transactions=txns,
            valid_product_ids={"P1"},
            logger=logger,
        )
        self.assertEqual(processed, 1)
        self.assertEqual(totals["P1"], 1)
        self.assertTrue(any("Invalid transaction date" in r.getMessage() for r in handler.records))

    def test_negative_quantity_ignored(self):
        logger, handler = self._logger()
        txns = [
            SalesTransaction("T1", "P1", "2024-04-01", -2),
            SalesTransaction("T2", "P1", "2024-04-02", 4),
        ]
        totals, processed = aggregate_sales_for_april_2024(
            transactions=txns,
            valid_product_ids={"P1"},
            logger=logger,
        )
        self.assertEqual(processed, 1)
        self.assertEqual(totals["P1"], 4)
        self.assertTrue(any("Negative quantity" in r.getMessage() for r in handler.records))

    def test_non_april_2024_dates_ignored(self):
        logger, handler = self._logger()
        txns = [
            SalesTransaction("T1", "P1", "2024-03-31", 5),  # March
            SalesTransaction("T2", "P1", "2024-04-01", 3),  # April
            SalesTransaction("T3", "P1", "2024-05-01", 2),  # May
        ]
        totals, processed = aggregate_sales_for_april_2024(
            transactions=txns,
            valid_product_ids={"P1"},
            logger=logger,
        )
        self.assertEqual(processed, 1)
        self.assertEqual(totals["P1"], 3)

    def test_unknown_product_id_ignored(self):
        logger, handler = self._logger()
        txns = [
            SalesTransaction("T1", "P1", "2024-04-01", 5),
            SalesTransaction("T2", "P999", "2024-04-02", 10),  # Unknown product
            SalesTransaction("T3", "P2", "2024-04-03", 3),
        ]
        totals, processed = aggregate_sales_for_april_2024(
            transactions=txns,
            valid_product_ids={"P1", "P2"},
            logger=logger,
        )
        self.assertEqual(processed, 2)
        self.assertEqual(totals["P1"], 5)
        self.assertEqual(totals["P2"], 3)
        self.assertTrue(any("Unknown product_id" in r.getMessage() for r in handler.records))
