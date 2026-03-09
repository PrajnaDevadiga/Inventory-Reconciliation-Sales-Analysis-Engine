import tempfile
import unittest
from pathlib import Path

from src.loader import InventoryItem, SalesTransaction, iter_sales_transactions_csv, read_inventory_csv


class LoaderTests(unittest.TestCase):
    def test_read_inventory_csv_valid(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("product_id,product_name,current_stock,unit_price,category\n")
            f.write("P1,Product1,10,25.50,Category1\n")
            f.write("P2,Product2,20,30.00,Category2\n")
            temp_path = f.name

        try:
            inventory = read_inventory_csv(temp_path)
            self.assertEqual(len(inventory), 2)
            self.assertIn("P1", inventory)
            self.assertIn("P2", inventory)
            self.assertEqual(inventory["P1"].product_name, "Product1")
            self.assertEqual(inventory["P1"].current_stock, 10)
            self.assertEqual(inventory["P1"].unit_price, 25.50)
        finally:
            Path(temp_path).unlink()

    def test_read_inventory_csv_skips_malformed_rows(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("product_id,product_name,current_stock,unit_price,category\n")
            f.write("P1,Product1,10,25.50,Category1\n")
            f.write(",Product2,20,30.00,Category2\n")  # missing product_id
            f.write("P3,Product3,15,40.00,Category3\n")  # valid
            f.write("P4,Product4,invalid,50.00,Category4\n")  # invalid stock
            f.write("P5,Product5,25,invalid,Category5\n")  # invalid price
            temp_path = f.name

        try:
            inventory = read_inventory_csv(temp_path)
            # P1 and P3 should be valid (P3 has valid data)
            self.assertEqual(len(inventory), 2)
            self.assertIn("P1", inventory)
            self.assertIn("P3", inventory)
        finally:
            Path(temp_path).unlink()

    def test_read_inventory_csv_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("product_id,product_name,current_stock,unit_price,category\n")
            temp_path = f.name

        try:
            inventory = read_inventory_csv(temp_path)
            self.assertEqual(len(inventory), 0)
        finally:
            Path(temp_path).unlink()

    def test_iter_sales_transactions_csv_valid(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("transaction_id,product_id,transaction_date,quantity_sold\n")
            f.write("T1,P1,2024-04-01,5\n")
            f.write("T2,P2,2024-04-02,10\n")
            temp_path = f.name

        try:
            transactions = list(iter_sales_transactions_csv(temp_path))
            self.assertEqual(len(transactions), 2)
            self.assertEqual(transactions[0].transaction_id, "T1")
            self.assertEqual(transactions[0].product_id, "P1")
            self.assertEqual(transactions[0].quantity_sold, 5)
        finally:
            Path(temp_path).unlink()

    def test_iter_sales_transactions_csv_skips_malformed_rows(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("transaction_id,product_id,transaction_date,quantity_sold\n")
            f.write("T1,P1,2024-04-01,5\n")
            f.write(",P2,2024-04-02,10\n")  # missing transaction_id
            f.write("T3,,2024-04-03,15\n")  # missing product_id
            f.write("T4,P4,,20\n")  # missing date
            f.write("T5,P5,2024-04-05,invalid\n")  # invalid quantity
            temp_path = f.name

        try:
            transactions = list(iter_sales_transactions_csv(temp_path))
            # Only T1 should be valid
            self.assertEqual(len(transactions), 1)
            self.assertEqual(transactions[0].transaction_id, "T1")
        finally:
            Path(temp_path).unlink()

    def test_iter_sales_transactions_csv_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("transaction_id,product_id,transaction_date,quantity_sold\n")
            temp_path = f.name

        try:
            transactions = list(iter_sales_transactions_csv(temp_path))
            self.assertEqual(len(transactions), 0)
        finally:
            Path(temp_path).unlink()
