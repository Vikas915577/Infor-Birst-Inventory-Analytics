# Infor Birst Blueprint — Inventory & Stock Risk Analytics

> **Project state:** This is a synthetic-data portfolio and implementation blueprint. It is not evidence of a deployed Birst dashboard. The actual Birst build must be completed and reconciled in a personal practice space before claiming it as implemented.

## The user story
As an inventory planner or warehouse operations lead, I need to identify the riskiest SKU–warehouse combinations, understand what caused the flag, and prioritize a replenishment review—without the dashboard automatically placing orders.

Read [`DDD_USER_STORY_AND_ACCEPTANCE_CRITERIA.md`](DDD_USER_STORY_AND_ACCEPTANCE_CRITERIA.md) for decision owner, acceptance criteria, metric definitions and the complete Display → Diagnose → Decide flow.

## Data model
**Fact:** `fact_inventory_snapshot`, at one row per snapshot date × SKU × warehouse.

**Dimensions:**
- `dim_product`: SKU, product name, category, supplier, synthetic unit cost, reorder point, supplier lead time.
- `dim_warehouse`: warehouse name and region.

**Joins:** Fact SKU → Product SKU; Fact Warehouse ID → Warehouse ID. Confirm that each dimension key is unique and row count is unchanged after joining.

**Business-friendly subject area:** `Inventory & Replenishment`, with only required attributes/measures. Infor documents that subject areas expose attributes and measures for reporting, and recommends custom subject areas with user-friendly labeling and only relevant fields.

## Proposed DDD dashboard pages

### Page 1 — DISPLAY: Inventory Overview
**Question:** Is current inventory risk material?
- KPI dashlets: snapshot date, on-hand units, estimated inventory value, below-reorder records, stockout-risk records, out-of-stock records.
- Visuals: risk records by warehouse; inventory value by category.
- Shared filters: snapshot date, region, warehouse, category, risk status. In the website preview, the same scope updates KPI tiles and category/warehouse charts; implement equivalent filter associations across Birst dashlets and verify each association.
- Always show the single snapshot scope; do not show trends until multiple dated snapshots exist.

### Page 2 — DIAGNOSE: Risk Drivers
**Question:** Where is the risk, and what triggered it?
- Coverage vs supplier lead-time scatter plot.
- Warehouse × category risk matrix or summary.
- SKU detail report with stock, demand, days of supply, lead time, reorder point, supplier, unit cost and risk reason.
- Filters: warehouse, region, category, supplier, risk status. The website preview also supports free-text search and all-records/flagged-only scope.
- Drill across from a summary row to detailed SKU records where supported by the tenant/design.

### Page 3 — DECIDE: Replenishment Review Queue
**Question:** Which records require review first, and what must be checked?
- P1: out of stock or days of supply below lead time.
- P2: on hand at/below reorder point but not P1.
- P3: monitor; kept out of the urgent queue.
- Table fields: priority, SKU, product, warehouse, on hand, daily demand, days of supply, lead time, reorder point, illustrative review quantity, decision basis, suggested next step.
- Add a text block explaining the safety buffer assumption and the need to validate open POs, supplier pack sizes/MOQs, forecast, safety stock, budget and approvals.
- Export/report controls can be used to hand the queue to an authorized inventory owner; this project does not automate purchase orders.

## Metric definitions
- **Days of Supply** = on-hand quantity ÷ average daily demand; if demand is zero/undefined, treat coverage as unavailable, flag zero stock separately, and validate the demand source before relying on a quantity estimate.
- **Stockout Risk** = days of supply < supplier lead time.
- **Below Reorder Point** = on-hand quantity ≤ reorder point.
- **Inventory Value** = on-hand quantity × synthetic unit cost.
- **Illustrative Review Qty** = max(0, ceil(avg daily demand × (lead time + 7-day buffer) − on hand)). The buffer is a demo assumption, not a company policy.
- Counts are at SKU–warehouse row grain, not necessarily distinct SKU counts.

## Recommended Infor Birst build sequence
1. Use a personal practice/demo space and only the included synthetic CSV files.
2. Import `dim_product.csv`, `dim_warehouse.csv`, `fact_inventory_snapshot.csv` as sources using the approved file connection/upload workflow.
3. Check types: IDs as text, snapshot date as date, quantities/reorder/lead time as numeric, demand/cost as decimal.
4. Define fact-to-dimension joins, confirm unique dimension keys and row count remains 480.
5. Create a custom subject area with user-friendly field names and measures; hide technical fields not needed by dashboard users.
6. Build Visualizer reports for Display KPIs, risk by warehouse, category inventory value, coverage vs lead time, and the replenishment-review table.
7. Create the 3 dashboard pages and shared/associated filters. Infor documentation supports pages with report dashlets, filters and KPI dashlets; filters let users explore subsets and ranges. Map each filter to the relevant reports/KPIs and check the resulting values—not every filter association is automatic.
8. Test filter propagation, drill-down/drill-across, exports, zero-demand behavior and totals after joins. For zero/undefined demand, display days of supply as unavailable and direct the user to verify the demand source rather than treating a review quantity of zero as proof that no replenishment is needed.
9. Reconcile the same filter selections to `kpi_summary.csv`, `warehouse_risk_summary.csv`, `category_summary.csv`, and `priority_replenishment_list.csv`.
10. Reconcile filtered results for at least one warehouse, one category, one risk status and one search case; verify totals agree across KPI, Diagnose and Decide outputs. Capture your own screenshots only after real Birst reports are built and tested. Update the README with what you personally implemented, the date and any deviations.

## Validation baseline for the included generated sample
- Fact rows: 480
- SKUs: 120
- Warehouses: 4
- On-hand units: 81,978
- Inventory value: 9,654,146.75 synthetic currency units
- Stockout-risk records: 220 (45.8% of SKU–warehouse records)
- At/below reorder point: 161 (33.5% of records)

## Data quality and operational limitations
- All data is synthetic; no real supplier/customer inventory is represented.
- Only one snapshot exists; time trends or stock movement cannot be inferred.
- Inventory value uses generated unit costs with no declared currency; it is illustrative.
- The heuristic does not model forecast uncertainty, seasonal demand, safety stock policy, open purchase orders, order multiples or supplier constraints.
- Counts must be labeled “records” unless a distinct-SKU metric is explicitly calculated.
- Keep data refresh date and snapshot date separate.

## Official Infor references
- [Creating dashboards](https://docs.infor.com/birst/latest/en-us/birstolh/dashboards_user/ifj1655271234451.html)
- [Adding KPI dashlets](https://docs.infor.com/birst/latest/en-us/birstolh/dashboards_user/jmt1655271239123.html)
- [Dashboard filters](https://docs.infor.com/birst/2026.10/en-us/birstolh/dashboards_user/ieb1655271241138.html)
- [Visualizer filtering](https://docs.infor.com/birst/2025.x/en-us/birstolh/reports_user/xah1655271135431.html)
- [Subject areas](https://docs.infor.com/birst/latest/en-us/birstolh/reports_user/bha1655271152572.html)
- [Infor Analytics with Birst](https://developer.infor.com/tutorials/analytics-with-birst)
- [Infor file connection tutorial](https://developer.infor.com/tutorials/analytics/how-to-connect-to-a-file)

## DDD research note
Display → Diagnose → Decide is described in Infor’s value-based design material as a guided analytics information architecture. In this project, Display surfaces the signal, Diagnose explains the risk by dimension and SKU, and Decide turns that diagnosis into a prioritized review queue with explicit assumptions.
