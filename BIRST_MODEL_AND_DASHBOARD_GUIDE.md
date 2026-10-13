# Infor Birst Build Guide — Inventory & Stock Risk Analytics

## Project status and honesty note
This repository contains a **Birst-oriented portfolio blueprint** built around synthetic data. It is not a deployed Birst dashboard yet. Use it to demonstrate how you would structure and validate a BI reporting solution; after building it in your Birst account, add your own screenshot and test results. Never upload work/client data.

## Source CSVs
- `data/source_synthetic/dim_product.csv` — one row per SKU.
- `data/source_synthetic/dim_warehouse.csv` — one row per warehouse.
- `data/source_synthetic/fact_inventory_snapshot.csv` — one row per SKU × warehouse × snapshot date.

Starter grain: 480 fact records, 120 SKUs, 4 warehouses, snapshot date 2026-10-12.

## Logical model
Use `fact_inventory_snapshot` as the fact table. Join `sku_id` to `dim_product.sku_id` (many fact rows to one product row), and `warehouse_id` to `dim_warehouse.warehouse_id` (many fact rows to one warehouse row). Confirm each fact row joins once; otherwise totals can inflate.

## Suggested subject area: Inventory & Replenishment
**Attributes:** Snapshot Date, SKU ID, Product Name, Category, Supplier, Warehouse Name, Region.

**Measures:** On-hand Units = SUM(on_hand_qty); Inventory Value = SUM(on_hand_qty × unit_cost); Inventory Records = COUNT(snapshot_id); Records Below Reorder Point = count of rows with on_hand_qty <= reorder_point; Records at Stockout Risk = count of rows where days_of_supply < lead_time_days; Out-of-stock Records = count of rows with on_hand_qty = 0.

Derived calculations: Days of Supply = on_hand_qty / avg_daily_demand (handle zero demand); Stockout Risk = Days of Supply < Lead Time; Below Reorder Point = On-hand Qty <= Reorder Point. These are simplified demo rules, not production replenishment policy.

## Suggested dashboard pages
1. **Inventory Overview:** KPI tiles for On-hand Units, Inventory Value, Below Reorder Point, Stockout Risk. Charts for risk records by warehouse and value by category. Filters: Snapshot Date, Region, Warehouse, Category.
2. **Replenishment Priority:** table of SKU, category, warehouse, stock, demand, days of supply, reorder point, lead time, status, supplier. Sort stockouts first then lowest coverage. Filters: Warehouse, Category, Supplier, Risk Status.
3. **Risk Drivers:** scatter Days of Supply vs Lead Time plus risk counts by warehouse/category.

## Build steps in Infor Birst
1. Open a practice/demo space; only use this synthetic data.
2. Upload the three CSVs as sources and verify column data types.
3. Define joins using `sku_id` and `warehouse_id`; validate join row counts.
4. Organize relevant attributes and measures in a user-friendly subject area.
5. Build Visualizer reports for risk by warehouse, value by category, coverage vs lead time and replenishment priority.
6. Add those reports to a dashboard; add KPI tiles and filters.
7. Compare totals against `outputs/kpi_summary.csv` and `outputs/warehouse_risk_summary.csv`.
8. Test filter propagation, zero demand, nulls, export and refresh; add your own screenshot only after doing this in Birst.

## Validation values for unchanged demo data
- Fact records: 480
- On-hand units: 81,978
- Inventory value: 9,654,146.75 synthetic currency units

## Official Infor references
- Dashboards: https://docs.infor.com/birst/latest/en-us/birstolh/dashboards_user/ifj1655271234451.html
- Visualizer filters: https://docs.infor.com/birst/2025.x/en-us/birstolh/reports_user/xah1655271135431.html
- BQL concepts: https://docs.infor.com/birst/latest/en-us/birstolh/birstug_bqlref/acc1717688368889.html
- Subject areas: https://docs.infor.com/birst/latest/en-us/birstolh/reports_user/bha1655271152572.html
