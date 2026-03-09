from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Sequence, Tuple

from .loader import InventoryItem


@dataclass(frozen=True)
class ReconciledInventoryRow:
    product_id: str
    product_name: str
    category: str
    current_stock: int
    total_sold_quantity: int
    final_stock: int
    stock_status: str
    total_sales_value: Decimal


def compute_stock_status(final_stock: int) -> str:
    if final_stock == 0:
        return "OUT_OF_STOCK"
    if 1 <= final_stock <= 10:
        return "LOW_STOCK"
    return "AVAILABLE"


def reconcile_inventory(
    inventory: Dict[str, InventoryItem],
    total_sold_by_product: Dict[str, int],
    logger: logging.Logger,
) -> Tuple[List[ReconciledInventoryRow], Decimal]:
    """
    Applies inventory reconciliation & transformations.

    - final_stock = current_stock - total_sold_quantity
    - if final_stock < 0 => set 0 and log STOCK_ERROR
    - total_sales_value = total_sold_quantity * unit_price
    """
    rows: List[ReconciledInventoryRow] = []
    total_sales_value = Decimal("0")

    for product_id in sorted(inventory.keys()):
        item = inventory[product_id]
        sold = int(total_sold_by_product.get(product_id, 0))
        raw_final = item.current_stock - sold
        final_stock = raw_final
        if raw_final < 0:
            final_stock = 0
            logger.error(
                "STOCK_ERROR: negative final stock corrected to 0: product_id=%s current_stock=%s sold=%s",
                product_id,
                item.current_stock,
                sold,
            )

        stock_status = compute_stock_status(final_stock)
        sales_value = (Decimal(sold) * item.unit_price) if sold > 0 else Decimal("0")
        total_sales_value += sales_value

        rows.append(
            ReconciledInventoryRow(
                product_id=product_id,
                product_name=item.product_name,
                category=item.category,
                current_stock=item.current_stock,
                total_sold_quantity=sold,
                final_stock=final_stock,
                stock_status=stock_status,
                total_sales_value=sales_value,
            )
        )

    return rows, total_sales_value


def low_and_out_of_stock_product_ids(
    rows: Sequence[ReconciledInventoryRow],
) -> Tuple[List[str], List[str]]:
    low: List[str] = []
    out: List[str] = []
    for r in rows:
        if r.stock_status == "LOW_STOCK":
            low.append(r.product_id)
        elif r.stock_status == "OUT_OF_STOCK":
            out.append(r.product_id)
    return low, out

