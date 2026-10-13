# Infor Birst Inventory Analytics — Display → Diagnose → Decide

**A decision-focused BI portfolio project** built around an inventory planner’s user story. It uses SQL, Python, synthetic inventory data, and a step-by-step Infor Birst implementation blueprint.

> **Data disclosure:** Every supplied record is synthetic demonstration data. The repository documents how to build and validate a Birst dashboard; it is not a claim that a live Birst dashboard has already been deployed.

## User story
As an inventory planner, I need to see which SKU–warehouse combinations are exposed to stockout risk, understand why they are flagged, and prioritize a replenishment review—so I can investigate before stock coverage falls below supplier lead time.

## Display → Diagnose → Decide
| Stage | User question | Birst page | Main outputs |
|---|---|---|---|
| **Display** | Is current inventory risk material? | Inventory Overview | On-hand units, estimated value, below-reorder records, stockout-risk records, out-of-stock records |
| **Diagnose** | Where is the risk and why? | Risk Diagnosis | Warehouse/category risk breakdown, coverage-vs-lead-time chart, SKU detail and risk reason |
| **Decide** | What should the authorized user review first? | Replenishment Review Queue | P1/P2 prioritization, decision basis, suggested next step, illustrative review quantity |

Read [`DDD_USER_STORY_AND_ACCEPTANCE_CRITERIA.md`](DDD_USER_STORY_AND_ACCEPTANCE_CRITERIA.md) for personas, acceptance criteria, rules and the decision owner.

## Open the dashboard-style project page
- GitHub Pages entry point: [`index.html`](index.html)
- The page is mobile-first and includes live filters for the generated review queue. It consumes `dashboard_data.json` and the image/CSV files in this repository.
- The website visualizes calculated outputs for demonstration; it is not an Infor-hosted dashboard.

## Data model
- `fact_inventory_snapshot`: one row per snapshot date × SKU × warehouse.
- `dim_product`: category, supplier, synthetic unit cost, reorder point, lead time.
- `dim_warehouse`: warehouse and region.

The starter data has 480 records, 120 SKUs, 4 warehouses, and one snapshot date: 2026-10-12. Because it is one snapshot, the project does **not** claim a historical trend.

## KPI definitions
- Days of Supply = on-hand quantity ÷ average daily demand.
- Stockout Risk = Days of Supply < supplier lead time.
- Below Reorder Point = on-hand quantity ≤ reorder point.
- Inventory Value = on-hand quantity × synthetic unit cost.
- Illustrative Review Quantity = max(0, ceil(daily demand × (lead time + 7-day buffer) − on-hand)). The 7-day buffer is a demo assumption, not company policy or an auto-order instruction.

## Tools
- **Infor Birst:** proposed fact/dimension model, subject area, KPI dashlets, Visualizer reports, dashboard filters and detail/review pages.
- SQL (PostgreSQL-compatible): joins, aggregation, data quality and decision queue.
- Python (pandas, NumPy, matplotlib): validation, risk flags, summaries, charts, JSON for the website.
- GitHub Pages: static project case-study page (separate from a live Birst dashboard).

## Run locally
Python 3.10+ recommended; run commands from this folder:

```bash
python -m pip install -r requirements.txt
python analyze_inventory.py
python -m unittest test_inventory_data -v
```

The script regenerates CSV output summaries, charts, `findings.txt`, and `dashboard_data.json` in the root. Four or more tests validate keys, joins, recommendation output and JSON reconciliation.

## Included files
- `index.html` — interactive, mobile-friendly DDD case-study page.
- `DDD_USER_STORY_AND_ACCEPTANCE_CRITERIA.md` — user story, decision owner and definition of done.
- `BIRST_MODEL_AND_DASHBOARD_GUIDE.md` — Birst-specific DDD dashboard plan and build steps.
- `RESEARCH_REFERENCES.md` — official Birst documentation and DDD reference notes.
- `analyze_inventory.py`, `test_inventory_data.py`, `requirements.txt` — reproducible code/tests.
- `01_schema_postgresql.sql`, `02_inventory_kpi_queries.sql`, `03_data_quality_checks.sql` — SQL schema/queries/quality checks.
- Source CSVs, output CSVs, `dashboard_data.json`, findings and three charts.

## Sample results — generated data only
- 220/480 records (45.8%) have days of supply below lead time.
- 161/480 records (33.5%) are at/below reorder point.
- 81,978 on-hand units and 9,654,146.75 synthetic currency units of estimated inventory value.

These figures describe only the current generated sample and must not be represented as a real employer outcome.

## Decision safety and limitations
- P1: out of stock or days of supply below lead time.
- P2: on-hand at/below reorder point, unless already P1.
- P3: no current threshold crossed.
- The suggested quantity is an illustrative review aid. Validate existing purchase orders, safety stock, forecast/seasonality, supplier MOQ/pack size, budget and approvals before acting. The dashboard does not place purchase orders.
- Counts are SKU–warehouse records, not unique SKU counts unless distinct-counted.
- Data is synthetic. Never commit private employer/client data.

## Build the actual Birst dashboard
1. Open a practice/demo Birst space; import the three source CSVs.
2. Create the fact/dimension joins; confirm row count remains 480.
3. Define a user-friendly `Inventory & Replenishment` subject area.
4. Build the 3 DDD dashboard pages and filters according to `BIRST_MODEL_AND_DASHBOARD_GUIDE.md`.
5. Reconcile Birst KPIs to `kpi_summary.csv`, `warehouse_risk_summary.csv`, and `category_summary.csv`.
6. Test filters, detail navigation, report exports and zero-demand behavior.
7. Add Birst screenshots to this repo only after you actually build and validate the dashboard.

## Research
- [Infor Birst dashboard creation](https://docs.infor.com/birst/latest/en-us/birstolh/dashboards_user/ifj1655271234451.html)
- [KPI dashlets](https://docs.infor.com/birst/latest/en-us/birstolh/dashboards_user/jmt1655271239123.html)
- [Dashboard filters](https://docs.infor.com/birst/2026.10/en-us/birstolh/dashboards_user/ieb1655271241138.html)
- [Subject areas](https://docs.infor.com/birst/latest/en-us/birstolh/reports_user/bha1655271152572.html)
- [Infor Display → Diagnose → Decide reference (VBD white paper)](https://dam.infor.com/api/public/content/12f4f63a51784e6d9c0046b63385c2fd?v=b0eacc16)
