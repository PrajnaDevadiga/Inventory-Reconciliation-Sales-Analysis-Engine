from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Dict, Iterable, Iterator, Optional


@dataclass(frozen=True)
class InventoryItem:
    product_id: str
    product_name: str
    current_stock: int
    unit_price: Decimal
    category: str


@dataclass(frozen=True)
class SalesTransaction:
    transaction_id: str
    product_id: str
    transaction_date: str
    quantity_sold: int


def _safe_int(value: str) -> Optional[int]:
    try:
        return int(value)
    except Exception:
        return None


def _safe_decimal(value: str) -> Optional[Decimal]:
    try:
        return Decimal(value)
    except Exception:
        return None


def read_inventory_csv(path: str | Path) -> Dict[str, InventoryItem]:
    """
    Reads inventory.csv into a dict keyed by product_id.
    Skips malformed rows (caller handles logging if desired).
    """
    p = Path(path)
    inventory: Dict[str, InventoryItem] = {}
    with p.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row:
                continue
            product_id = (row.get("product_id") or "").strip()
            if not product_id:
                continue

            product_name = (row.get("product_name") or "").strip()
            category = (row.get("category") or "").strip()
            current_stock = _safe_int((row.get("current_stock") or "").strip())
            unit_price = _safe_decimal((row.get("unit_price") or "").strip())
            if current_stock is None or unit_price is None:
                continue

            inventory[product_id] = InventoryItem(
                product_id=product_id,
                product_name=product_name,
                current_stock=current_stock,
                unit_price=unit_price,
                category=category,
            )
    return inventory


def iter_sales_transactions_csv(path: str | Path) -> Iterator[SalesTransaction]:
    """
    Streams sales_transactions.csv rows as SalesTransaction.
    Skips malformed rows (caller handles logging if desired).
    """
    p = Path(path)
    with p.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row:
                continue
            transaction_id = (row.get("transaction_id") or "").strip()
            product_id = (row.get("product_id") or "").strip()
            transaction_date = (row.get("transaction_date") or "").strip()
            quantity_sold = _safe_int((row.get("quantity_sold") or "").strip())
            if not transaction_id or not product_id or not transaction_date or quantity_sold is None:
                continue
            yield SalesTransaction(
                transaction_id=transaction_id,
                product_id=product_id,
                transaction_date=transaction_date,
                quantity_sold=quantity_sold,
            )

