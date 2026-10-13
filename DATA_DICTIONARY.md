# Data Dictionary and Data Disclosure

Every CSV in `source_synthetic` is generated synthetic data created for this portfolio project. It is not company/client data.

## `dim_product.csv`
- `sku_id`: unique generated SKU key.
- `product_name`, `category`, `supplier`: generated descriptive attributes.
- `unit_cost`: synthetic unit cost; no currency specified.
- `reorder_point`: synthetic stock threshold.
- `lead_time_days`: synthetic supplier lead-time assumption.

## `dim_warehouse.csv`
- `warehouse_id`: generated unique warehouse key.
- `warehouse_name`, `region`: generated labels.

## `fact_inventory_snapshot.csv`
- `snapshot_id`: unique fact record key.
- `snapshot_date`: date of generated snapshot.
- `sku_id`, `warehouse_id`: keys to dimensions.
- `on_hand_qty`: generated on-hand quantity.
- `avg_daily_demand`: generated average daily demand.

**Grain:** one row per SKU × warehouse × snapshot date. The starter data contains one snapshot date and cannot support historical trend claims.
