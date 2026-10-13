# Data dictionary

All source data is generated synthetic demo data, not employer or client data.

- `dim_product.csv`: `sku_id`, product name, category, supplier, synthetic unit cost, reorder point, supplier lead time in days.
- `dim_warehouse.csv`: warehouse ID/name and region.
- `fact_inventory_snapshot.csv`: snapshot ID/date, SKU key, warehouse key, on-hand quantity and synthetic average daily demand.

Grain: one row per SKU × warehouse × snapshot date. Inventory value = quantity × synthetic unit cost. Days of supply = on-hand quantity ÷ average daily demand.
