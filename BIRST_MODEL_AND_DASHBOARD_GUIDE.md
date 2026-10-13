# Infor Birst Build Guide — Inventory & Stock Risk Analytics

## Project status
This is a Birst-oriented portfolio blueprint using synthetic data, not an already-deployed dashboard. Use a personal practice space only.

## Source files
All CSVs are in the repository root: `dim_product.csv`, `dim_warehouse.csv`, and `fact_inventory_snapshot.csv`. The fact grain is one row per SKU × warehouse × snapshot date (480 records, 120 SKUs, 4 warehouses, snapshot date 2026-10-12).

## Logical model / subject area
Join `fact_inventory_snapshot.sku_id` to `dim_product.sku_id`, and `warehouse_id` to `dim_warehouse.warehouse_id`. Subject area: **Inventory & Replenishment**.

**Attributes:** Snapshot Date, SKU ID, Product Name, Category, Supplier, Warehouse Name, Region.

**Measures:** On-hand Units = SUM(on_hand_qty); Inventory Value = SUM(on_hand_qty × unit_cost); Inventory Records = COUNT(snapshot_id); Below Reorder Point = count where on_hand_qty <= reorder_point; Stockout Risk = count where days of supply < lead time; Out of Stock = count where on_hand_qty = 0.

**Derived calculations:** Days of Supply = on_hand_qty / avg_daily_demand (handle zero demand). Stockout Risk = Days of Supply < Supplier Lead Time. Below Reorder Point = On-hand Quantity <= Reorder Point. These rules are simplified portfolio heuristics, not production policy.

## Suggested dashboard pages
1. **Inventory Overview:** KPI tiles for on-hand units, inventory value, below-reorder records and stockout-risk records; charts for risk by warehouse and value by category; filters for snapshot date, region, warehouse and category.
2. **Replenishment Priority:** SKU, category, warehouse, stock, demand, days of supply, reorder point, lead time, status and supplier; prioritize out-of-stock and lowest-coverage records.
3. **Risk Drivers:** scatter plot of days of supply vs lead time plus risk counts by warehouse/category.

## Build steps
1. Upload the three root CSVs to a personal Birst demo space. Infor supports CSV/file source workflows.
2. Verify data types and define joins; validate that fact row count remains 480 after joins.
3. Add attributes/measures to a user-friendly subject area.
4. Build Visualizer reports for risk by warehouse, inventory value by category, coverage vs lead time, and the replenishment table.
5. Add reports to dashboard pages with KPI tiles and filters.
6. Reconcile totals with root `kpi_summary.csv`, `warehouse_risk_summary.csv`, and `category_summary.csv`.
7. Test filter propagation, zero demand, nulls, export and refresh; add screenshots only after validation.

## Expected demo controls
- Fact rows: 480
- On-hand units: 81,978
- Inventory value: 9,654,146.75 synthetic currency units

## Official references
- [Infor Analytics with Birst](https://developer.infor.com/tutorials/analytics-with-birst)
- [How to connect to a file](https://developer.infor.com/tutorials/analytics/how-to-connect-to-a-file)
- [Birst dashboards](https://docs.infor.com/birst/latest/en-us/birstolh/dashboards_user/ifj1655271234451.html)
- [Visualizer filters](https://docs.infor.com/birst/2025.x/en-us/birstolh/reports_user/xah1655271135431.html)
