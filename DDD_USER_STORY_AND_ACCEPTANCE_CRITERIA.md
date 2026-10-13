# User Story & Acceptance Criteria — Display → Diagnose → Decide

## Primary user story
**As an inventory planner or warehouse operations lead, I want to see which SKU–warehouse combinations are most exposed to stockout risk, understand why they are flagged, and receive a transparent replenishment-review queue, so I can prioritize investigation before stock coverage falls below supplier lead time.**

## Users and decision
- **Primary user:** Inventory planner / supply chain analyst.
- **Secondary user:** Warehouse manager.
- **Decision supported:** Which SKU–warehouse records should be reviewed first, and what information must be checked before any order is raised?
- **Decision owner:** The authorized inventory/procurement user—not the dashboard.
- **Data scope:** One generated snapshot date, SKU × warehouse grain. The demo cannot claim historical trends.

## DDD interaction journey

### 1. DISPLAY — What needs attention?
**Question:** Is inventory risk material in the current snapshot?

Display the small set of KPIs that answer that question:
- Snapshot date and record count (show data scope/freshness context).
- On-hand units.
- Estimated inventory value = quantity × synthetic unit cost.
- Records below reorder point.
- Records at stockout risk (days of supply < lead time).
- Out-of-stock records.

**Birst design:** Page 1, *Inventory Overview*: KPI dashlets, risk-by-warehouse chart, inventory-value-by-category chart, and global snapshot/region/warehouse/category filters. Infor documents dashboard pages with reports, filters, and KPI dashlets.

### 2. DIAGNOSE — Where is the risk, and why?
**Question:** Which product/warehouse combination drives the signal?

Allow users to filter by warehouse, region, category, supplier and risk status, then inspect the SKU detail:
- On-hand quantity vs reorder point.
- Average daily demand assumption.
- Days of supply vs supplier lead time.
- Unit cost and estimated inventory value.
- Risk reason and source snapshot date.

**Birst design:** Page 2, *Risk Diagnosis*: warehouse/category breakdowns, coverage-vs-lead-time scatter plot, sortable SKU detail report, and drill-across from summary to a replenishment detail page. Subject areas should expose business-friendly names and only relevant attributes/measures.

### 3. DECIDE — What should happen next?
**Question:** What should the authorized user review first?

Create a transparent *Review Queue*:
- **P1 — Urgent review:** out of stock or days of supply below supplier lead time.
- **P2 — Replenishment review:** at or below reorder point, but not already P1.
- **P3 — Monitor:** no current threshold crossed (shown for context, not in the urgent queue).

Each flagged row includes a decision basis, suggested next step, and an **illustrative review quantity** calculated as:

`max(0, ceil(avg_daily_demand × (lead_time_days + 7) − on_hand_qty))`

The 7-day buffer is a declared demo assumption. The quantity is not an auto-purchase order or an operational recommendation until an owner validates safety stock, forecast variability, open purchase orders, minimum order quantity, supplier pack sizes, budget, and approval policy.

**Birst design:** Page 3, *Replenishment Review*: P1/P2 queue, drill-across to row details, filter cards, export control, text note with assumptions, and an explicit owner/review process outside this prototype. Birst supports dashboard filters and report/dashlet export; any actual workflow/PO action would require the organization’s approved system integration and controls.

## Acceptance criteria
1. **Metric consistency:** Dashboard KPI values reconcile to `kpi_summary.csv` for the same snapshot and filter context.
2. **No false time trend:** The interface clearly states that starter data contains one snapshot date; no trend chart is shown until multiple dated snapshots exist.
3. **Explainable risk:** Every P1/P2 row shows the rule that triggered its status.
4. **Priority order:** Out-of-stock records first, then stockout-risk records, then below-reorder records; sort by lowest days of supply within priority.
5. **Transparent quantity:** Suggested quantity shows the 7-day-buffer assumption and is labeled for review only.
6. **Filter consistency:** Warehouse, region, category and risk filters must update the same visible KPI/diagnosis/decision context in the actual Birst implementation.
7. **Join integrity:** Product and warehouse dimensions join many-to-one; fact row count remains unchanged after joins.
8. **Data quality:** Duplicate keys, missing dimension matches, negative quantities, missing cost and zero-demand division are checked.
9. **Privacy:** Only synthetic data is present. No employer/client records or screenshots are committed.
10. **Ownership:** The dashboard does not place or claim to place purchase orders; an authorized user makes the decision.

## Definition of done for Birst
- Load the CSVs in a personal Birst practice space.
- Configure the fact/dimension model and business-friendly subject area.
- Build the three DDD report pages with filters/drill-across as the tenant supports.
- Reconcile key KPIs and test filter behavior/exports.
- Capture real screenshots only after the implementation is built and verified.
- Record Birst version, refresh date, data snapshot date and known limitations in the README.
