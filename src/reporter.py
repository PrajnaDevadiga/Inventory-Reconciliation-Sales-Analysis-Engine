from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Sequence

from .inventory_engine import ReconciledInventoryRow


def write_inventory_reconciliation_csv(
    rows: Sequence[ReconciledInventoryRow],
    output_path: str | Path,
) -> None:
    p = Path(output_path)
    fieldnames = [
        "product_id",
        "product_name",
        "category",
        "current_stock",
        "total_sold_quantity",
        "final_stock",
        "stock_status",
        "total_sales_value",
    ]
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "product_id": r.product_id,
                    "product_name": r.product_name,
                    "category": r.category,
                    "current_stock": r.current_stock,
                    "total_sold_quantity": r.total_sold_quantity,
                    "final_stock": r.final_stock,
                    "stock_status": r.stock_status,
                    # keep JSON-friendly numeric formatting as a string in CSV
                    "total_sales_value": str(r.total_sales_value),
                }
            )


def write_sales_summary_json(
    *,
    output_path: str | Path,
    total_products: int,
    total_transactions_processed: int,
    total_sales_value: Decimal,
    low_stock_products: List[str],
    out_of_stock_products: List[str],
) -> None:
    p = Path(output_path)
    payload: Dict[str, object] = {
        "total_products": total_products,
        "total_transactions_processed": total_transactions_processed,
        "total_sales_value": float(total_sales_value),
        "low_stock_products": low_stock_products,
        "out_of_stock_products": out_of_stock_products,
    }
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")

