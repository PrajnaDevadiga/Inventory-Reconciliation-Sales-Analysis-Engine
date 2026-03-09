from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .inventory_engine import low_and_out_of_stock_product_ids, reconcile_inventory
from .loader import iter_sales_transactions_csv, read_inventory_csv
from .reporter import write_inventory_reconciliation_csv, write_sales_summary_json
from .sales_aggregator import aggregate_sales_for_april_2024


def configure_logger(log_path: str | Path) -> logging.Logger:
    logger = logging.getLogger("inventory")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Avoid duplicate handlers if main() is called multiple times (tests, etc.)
    if logger.handlers:
        return logger

    p = Path(log_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(p, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory reconciliation engine")
    parser.add_argument("--inventory", default=str(Path("data") / "inventory.csv"))
    parser.add_argument(
        "--transactions",
        default=str(Path("data") / "sales_transactions.csv"),
    )
    parser.add_argument("--out-inventory", default="inventory_reconciliation.csv")
    parser.add_argument("--out-summary", default="sales_summary.json")
    parser.add_argument("--log", default=str(Path("logs") / "inventory.log"))
    args = parser.parse_args()

    logger = configure_logger(args.log)

    inventory = read_inventory_csv(args.inventory)
    transactions = list(iter_sales_transactions_csv(args.transactions))

    totals, processed = aggregate_sales_for_april_2024(
        transactions=transactions,
        valid_product_ids=set(inventory.keys()),
        logger=logger,
    )

    rows, total_sales_value = reconcile_inventory(
        inventory=inventory,
        total_sold_by_product=totals,
        logger=logger,
    )
    low, out = low_and_out_of_stock_product_ids(rows)

    write_inventory_reconciliation_csv(rows, args.out_inventory)
    write_sales_summary_json(
        output_path=args.out_summary,
        total_products=len(inventory),
        total_transactions_processed=processed,
        total_sales_value=total_sales_value,
        low_stock_products=low,
        out_of_stock_products=out,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

