# Inventory & Stock Risk Analytics — Infor Birst Portfolio Project

**Live project page:** https://vikas915577.github.io/Infor-Birst-Inventory-Analytics/

**Goal:** Demonstrate inventory data modeling, SQL analysis, Python-based validation, and an implementation blueprint for **Infor Birst**.

> **Data disclosure:** All sample rows are synthetic demonstration data, not real company/client records. This repository contains a Birst implementation guide, not a claim that a dashboard is already deployed in Birst.

## Business questions
1. Which SKU–warehouse records have less stock coverage than supplier lead time?
2. Which records are at or below their reorder point?
3. How does estimated inventory value differ by category and warehouse?
4. Which items should be prioritized for replenishment review?

## Tools
- **Infor Birst:** model design, subject-area attributes/measures, Visualizer reports, KPI tiles and dashboard filters.
- **SQL (PostgreSQL-compatible):** joins, aggregation, replenishment prioritisation and data-quality checks.
- **Python:** pandas, NumPy and matplotlib for risk flags, summaries, charts and checks.

## Important: layout matches mobile upload
All source files and sample CSVs are in the repository root. The Python script and test use this flat layout, so the run instructions work after extracting this ZIP and uploading the files from the inner folder.

## Run locally
Python 3.10+ recommended.

```bash
python -m pip install -r requirements.txt
python analyze_inventory.py
python -m unittest test_inventory_data -v
```

The script reads `dim_product.csv`, `dim_warehouse.csv`, and `fact_inventory_snapshot.csv` from the current directory. It regenerates KPI summaries, replenishment rows, findings and charts in the same folder.

## Included files
- `index.html` — mobile-friendly GitHub Pages landing page.
- `dim_product.csv`, `dim_warehouse.csv`, `fact_inventory_snapshot.csv` — synthetic source data.
- `analyze_inventory.py` — repeatable Python analysis.
- `01_schema_postgresql.sql`, `02_inventory_kpi_queries.sql`, `03_data_quality_checks.sql` — SQL schema and analysis.
- `BIRST_MODEL_AND_DASHBOARD_GUIDE.md` — Birst model, measures, dashboard pages and validation plan.
- `kpi_summary.csv`, `warehouse_risk_summary.csv`, `category_summary.csv`, `priority_replenishment_list.csv`, `findings.txt` — generated demo outputs.
- `stockout_risk_by_warehouse.png`, `inventory_value_by_category.png`, `coverage_vs_lead_time.png` — generated charts.
- `DATA_DICTIONARY.md`, `requirements.txt`, `test_inventory_data.py`, `UPLOAD_FIX_GUIDE.md`.

## Sample findings (synthetic data only)
- 220 of 480 SKU–warehouse records (45.8%) have days of supply below supplier lead time.
- 161 of 480 records (33.5%) are at or below their reorder point.
- North Hub has the highest number of stockout-risk records (59).
- Electronics has the largest on-hand inventory value (3,262,097.64 synthetic currency units).

These numbers are generated from the sample dataset only, not real-world business results.

## Definitions and limitations
- Days of Supply = On-hand Quantity / Average Daily Demand.
- Stockout Risk = Days of Supply < Supplier Lead Time.
- Below Reorder Point = On-hand Quantity <= Reorder Point.
- Inventory Value = On-hand Quantity × Unit Cost.
- Counts are SKU–warehouse records, not necessarily distinct SKUs.
- Only one snapshot is included, so this is a single-date analysis, not a historical trend.
- The simplified risk rule omits safety stock, demand variation, open purchase orders and order multiples.

## Infor Birst dashboard plan
The guide describes an Inventory & Replenishment subject area, joins, attributes/measures, KPI tiles, Visualizer reports and filters. Import the CSVs into a practice Birst space and reconcile totals against the output files. Only add a Birst screenshot after building and testing it.

Official references: [Infor Analytics with Birst](https://developer.infor.com/tutorials/analytics-with-birst) · [How to connect to a file](https://developer.infor.com/tutorials/analytics/how-to-connect-to-a-file).

## Resume wording — only after you have reviewed and completed the work
**Inventory & Stock Risk Analytics | SQL, Python, Infor Birst (implementation blueprint)**
- Modeled inventory snapshot, product and warehouse data; analyzed stock coverage, reorder points and estimated inventory value.
- Designed a Birst implementation plan with subject-area attributes/measures, KPI tiles, Visualizer reports and dashboard filters.
- Evaluated replenishment-risk records using a clearly labelled synthetic dataset.

Do not claim a Birst dashboard was deployed until you have built and tested it in your own Birst environment.
