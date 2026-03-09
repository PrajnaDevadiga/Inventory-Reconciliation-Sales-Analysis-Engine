import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.main import configure_logger, main


class MainTests(unittest.TestCase):
    def test_configure_logger(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger = configure_logger(str(log_path))
            self.assertIsNotNone(logger)
            self.assertEqual(logger.name, "inventory")
            self.assertTrue(log_path.exists())
            # Close handlers to allow cleanup
            for handler in logger.handlers:
                handler.close()

    def test_configure_logger_no_duplicate_handlers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            logger1 = configure_logger(str(log_path))
            handler_count1 = len(logger1.handlers)
            logger2 = configure_logger(str(log_path))
            handler_count2 = len(logger2.handlers)
            # Should not add duplicate handlers
            self.assertEqual(handler_count1, handler_count2)
            # Close handlers to allow cleanup
            for handler in logger2.handlers:
                handler.close()

    @patch("src.main.read_inventory_csv")
    @patch("src.main.iter_sales_transactions_csv")
    @patch("src.main.aggregate_sales_for_april_2024")
    @patch("src.main.reconcile_inventory")
    @patch("src.main.low_and_out_of_stock_product_ids")
    @patch("src.main.write_inventory_reconciliation_csv")
    @patch("src.main.write_sales_summary_json")
    def test_main_function(self, mock_write_json, mock_write_csv, mock_low_out, mock_reconcile, mock_aggregate, mock_iter_sales, mock_read_inv):
        from decimal import Decimal
        from src.loader import InventoryItem, SalesTransaction

        # Setup mocks
        mock_read_inv.return_value = {
            "P1": InventoryItem("P1", "Product1", 10, Decimal("10.00"), "Cat1")
        }
        mock_iter_sales.return_value = [
            SalesTransaction("T1", "P1", "2024-04-01", 5)
        ]
        mock_aggregate.return_value = ({"P1": 5}, 1)
        mock_reconcile.return_value = ([], Decimal("50.00"))
        mock_low_out.return_value = ([], [])

        with tempfile.TemporaryDirectory() as tmpdir:
            inv_path = Path(tmpdir) / "inventory.csv"
            sales_path = Path(tmpdir) / "sales.csv"
            out_inv_path = Path(tmpdir) / "out_inv.csv"
            out_summary_path = Path(tmpdir) / "out_summary.json"
            log_path = Path(tmpdir) / "log.log"

            # Create dummy CSV files
            inv_path.write_text("product_id,product_name,current_stock,unit_price,category\nP1,Product1,10,10.00,Cat1\n")
            sales_path.write_text("transaction_id,product_id,transaction_date,quantity_sold\nT1,P1,2024-04-01,5\n")

            with patch("sys.argv", ["main.py", "--inventory", str(inv_path), "--transactions", str(sales_path), "--out-inventory", str(out_inv_path), "--out-summary", str(out_summary_path), "--log", str(log_path)]):
                result = main()
                self.assertEqual(result, 0)

            # Verify functions were called
            mock_read_inv.assert_called_once()
            mock_iter_sales.assert_called_once()
            mock_aggregate.assert_called_once()
            mock_reconcile.assert_called_once()
            mock_low_out.assert_called_once()
            mock_write_csv.assert_called_once()
            mock_write_json.assert_called_once()
