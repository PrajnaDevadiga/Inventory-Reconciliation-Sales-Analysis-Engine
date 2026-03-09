from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, Optional, Set, Tuple

from .loader import SalesTransaction


def parse_iso_date(value: str) -> Optional[date]:
    try:
        return date.fromisoformat(value)
    except Exception:
        return None


def is_april_2024(d: date) -> bool:
    return d.year == 2024 and d.month == 4


@dataclass(frozen=True)
class SalesAggregationResult:
    total_sold_by_product: Dict[str, int]
    total_transactions_processed: int
    total_sales_value: float  # computed later in inventory step; set here as 0.0


def aggregate_sales_for_april_2024(
    transactions: Iterable[SalesTransaction],
    valid_product_ids: Set[str],
    logger: logging.Logger,
) -> Tuple[Dict[str, int], int]:
    """
    Returns (total_sold_by_product_id, total_transactions_processed).

    Processing rules:
    - Only April 2024 transactions count as processed.
    - Invalid dates are ignored and logged.
    - Negative quantities are ignored and logged.
    - Unknown product_ids are ignored and logged.
    """
    totals: Dict[str, int] = {}
    processed = 0

    for t in transactions:
        d = parse_iso_date(t.transaction_date)
        if d is None:
            logger.warning(
                "Invalid transaction date skipped: transaction_id=%s date=%r",
                t.transaction_id,
                t.transaction_date,
            )
            continue
        if not is_april_2024(d):
            continue

        if t.quantity_sold < 0:
            logger.warning(
                "Negative quantity skipped: transaction_id=%s product_id=%s qty=%s",
                t.transaction_id,
                t.product_id,
                t.quantity_sold,
            )
            continue

        if t.product_id not in valid_product_ids:
            logger.warning(
                "Unknown product_id skipped: transaction_id=%s product_id=%s",
                t.transaction_id,
                t.product_id,
            )
            continue

        processed += 1
        totals[t.product_id] = totals.get(t.product_id, 0) + t.quantity_sold

    return totals, processed

