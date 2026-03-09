## Inventory Reconciliation & Sales Analysis Engine (Python)

### Overview
This project reads product inventory and daily sales transactions, filters and aggregates sales for **April 2024**, reconciles inventory levels, detects stock issues, and generates:

- `inventory_reconciliation.csv`
- `sales_summary.json`

### Business rules implemented
- **Sales filtering**
  - Only transactions in **April 2024** are considered.
  - Invalid dates are **ignored** and **logged**.
  - Negative quantities are **ignored** and **logged**.
- **Sales aggregation**
  - Total quantity sold is aggregated per `product_id`.
  - If a transaction references an unknown `product_id`, it is **ignored** and **logged**.
- **Inventory reconciliation**
  - `final_stock = current_stock - total_quantity_sold`
  - If `final_stock < 0`, it is set to `0` and the row is flagged as `STOCK_ERROR` in logs.
- **Stock status**
  - `final_stock == 0` → `OUT_OF_STOCK`
  - `1..10` → `LOW_STOCK`
  - `> 10` → `AVAILABLE`
- **Transformations**
  - Adds: `total_sold_quantity`, `final_stock`, `stock_status`, `total_sales_value`

### Project structure
```
data/
  inventory.csv
  sales_transactions.csv
src/
  loader.py
  sales_aggregator.py
  inventory_engine.py
  reporter.py
  main.py
tests/
  test_sales_aggregator.py
  test_inventory_engine.py
logs/
  inventory.log
inventory_reconciliation.csv
sales_summary.json
```

### Execution
From the project root:

```bash
python -m src.main
```

Outputs are written to:
- `inventory_reconciliation.csv`
- `sales_summary.json`
- logs: `logs/inventory.log`

### Run tests
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Coverage (optional)
If you install `coverage`, you can run:

```bash
coverage run -m unittest
coverage report -m
```

### Assumptions & edge cases handled
- Bad rows do not crash the app; they are skipped with a log entry.
- Transactions outside April 2024 are ignored (not counted as processed).
- Unknown product IDs are ignored and logged.
- Negative quantities are ignored and logged.
