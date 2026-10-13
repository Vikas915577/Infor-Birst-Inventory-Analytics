# Inventory & Stock Risk Analytics — Infor Birst Portfolio Project

**Goal:** Demonstrate inventory data modeling, SQL analysis, Python-based validation, and an implementation blueprint for **Infor Birst**, your primary BI-tool context.

> **Data disclosure:** All included sample rows are generated synthetic data, not real business records. This repository has a Birst model/dashboard guide; it does not claim that a dashboard has already been deployed in Birst.

## Business questions
1. Which SKU–warehouse records have less stock coverage than supplier lead time?
2. Which records are at/below reorder point?
3. How does estimated inventory value differ by category and warehouse?
4. Which items should be prioritized for replenishment review?

## Tools
- **Infor Birst:** proposed model, subject area, Visualizer reports, dashboard KPI tiles and filters.
- **SQL (PostgreSQL-compatible):** joins, aggregation, replenishment list, data quality.
- **Python:** pandas, NumPy and matplotlib for risk flags, summaries, charts and checks.

## Data model
`fact_inventory_snapshot` joins to `dim_product` on `sku_id` and to `dim_warehouse` on `warehouse_id`. One fact row represents one snapshot date × SKU × warehouse.

## Run the project
Python 3.10+ recommended.
```bash
python -m pip install -r requirements.txt
python python/analyze_inventory.py
python -m unittest discover -s tests -v
```

## Included outputs
- `outputs/kpi_summary.csv` — executive KPIs.
- `outputs/warehouse_risk_summary.csv` — warehouse risk summary.
- `outputs/category_summary.csv` — category totals and flags.
- `outputs/priority_replenishment_list.csv` — items to review.
- `outputs/findings.txt` and `outputs/charts/` — data-derived demo findings and charts.
- `birst/BIRST_MODEL_AND_DASHBOARD_GUIDE.md` — Birst-specific build steps, attributes/measures, suggested dashboard pages, and validation.

## Sample findings (synthetic data only)
- 220 of 480 SKU–warehouse snapshot records (45.8%) are below the calculated days-of-supply vs lead-time threshold.
- 161 of 480 records (33.5%) are at or below the product reorder point.
- North Hub has the highest number of stockout-risk records (59) in this generated example.
- Electronics has the largest on-hand inventory value (3,262,097.64 currency units) in this generated example.

## Definitions and limitations
- Days of Supply = On-hand Quantity / Average Daily Demand.
- Stockout Risk = Days of Supply < Supplier Lead Time.
- Below Reorder Point = On-hand Quantity <= Reorder Point.
- Inventory Value = On-hand Quantity × Unit Cost.
- Flag counts are SKU–warehouse records, not necessarily distinct SKUs.
- One snapshot is included, so this is a current-snapshot analysis, not a genuine time trend. The simplified rule omits safety stock, demand variation, open purchase orders and order multiples.

## Resume wording — use after reviewing and being able to explain it
**Inventory & Stock Risk Analytics | SQL, Python, Infor Birst (implementation blueprint)**
- Modeled inventory snapshot, product and warehouse data; analyzed stock coverage, reorder points and estimated inventory value using SQL and Python.
- Designed an Infor Birst implementation plan with subject-area attributes/measures, KPI tiles, Visualizer reports and dashboard filters.
- Evaluated replenishment-risk records by warehouse and category using a clearly labelled synthetic dataset.

Do not claim a Birst dashboard was implemented until you have built and tested it in your own Birst environment.

## GitHub upload
Create a public repository named `inventory-stock-risk-analytics`, upload the contents of this folder, and verify the README renders. Do not upload private client data or credentials. Once you build in Birst, add your own screenshot and record the validation you performed.
