import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from src.inventory_engine import ReconciledInventoryRow
from src.reporter import write_inventory_reconciliation_csv, write_sales_summary_json


class ReporterTests(unittest.TestCase):
    def test_write_inventory_reconciliation_csv(self):
        rows = [
            ReconciledInventoryRow(
                product_id="P1",
                product_name="Product1",
                category="Category1",
                current_stock=10,
                total_sold_quantity=5,
                final_stock=5,
                stock_status="LOW_STOCK",
                total_sales_value=Decimal("25.50"),
            ),
            ReconciledInventoryRow(
                product_id="P2",
                product_name="Product2",
                category="Category2",
                current_stock=20,
                total_sold_quantity=10,
                final_stock=10,
                stock_status="LOW_STOCK",
                total_sales_value=Decimal("30.00"),
            ),
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            temp_path = f.name

        try:
            write_inventory_reconciliation_csv(rows, temp_path)
            self.assertTrue(Path(temp_path).exists())

            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("product_id", content)
                self.assertIn("P1", content)
                self.assertIn("Product1", content)
                self.assertIn("25.50", content)
        finally:
            Path(temp_path).unlink()

    def test_write_sales_summary_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            temp_path = f.name

        try:
            write_sales_summary_json(
                output_path=temp_path,
                total_products=10,
                total_transactions_processed=50,
                total_sales_value=Decimal("1234.56"),
                low_stock_products=["P1", "P2"],
                out_of_stock_products=["P3"],
            )
            self.assertTrue(Path(temp_path).exists())

            with open(temp_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.assertEqual(data["total_products"], 10)
                self.assertEqual(data["total_transactions_processed"], 50)
                self.assertEqual(data["total_sales_value"], 1234.56)
                self.assertEqual(set(data["low_stock_products"]), {"P1", "P2"})
                self.assertEqual(set(data["out_of_stock_products"]), {"P3"})
        finally:
            Path(temp_path).unlink()
