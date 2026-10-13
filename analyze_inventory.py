#!/usr/bin/env python3
"""Inventory analytics with Display -> Diagnose -> Decide outputs for an Infor Birst portfolio demo.
All supplied source data is synthetic. Suggested quantities are illustrative review aids, not purchase orders.
"""
from pathlib import Path
import argparse, json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

REQUIRED_PRODUCT = {"sku_id", "product_name", "category", "supplier", "unit_cost", "reorder_point", "lead_time_days"}
REQUIRED_WAREHOUSE = {"warehouse_id", "warehouse_name", "region"}
REQUIRED_FACT = {"snapshot_id", "snapshot_date", "sku_id", "warehouse_id", "on_hand_qty", "avg_daily_demand"}
SAFETY_BUFFER_DAYS = 7  # explicit demo assumption; review before operational use


def analyze(data_dir: Path, output_dir: Path):
    p = pd.read_csv(data_dir / "dim_product.csv")
    w = pd.read_csv(data_dir / "dim_warehouse.csv")
    f = pd.read_csv(data_dir / "fact_inventory_snapshot.csv")
    for label, df, cols in [("product", p, REQUIRED_PRODUCT), ("warehouse", w, REQUIRED_WAREHOUSE), ("fact", f, REQUIRED_FACT)]:
        missing = cols - set(df.columns)
        if missing: raise ValueError(f"{label} file missing required columns: {sorted(missing)}")
    if not p.sku_id.is_unique: raise ValueError("dim_product.sku_id must be unique")
    if not w.warehouse_id.is_unique: raise ValueError("dim_warehouse.warehouse_id must be unique")
    if not f.snapshot_id.is_unique: raise ValueError("snapshot_id must be unique")
    if f[["snapshot_id", "snapshot_date", "sku_id", "warehouse_id"]].isna().any().any(): raise ValueError("Fact keys/date cannot be null")
    if (f.on_hand_qty < 0).any() or (f.avg_daily_demand < 0).any(): raise ValueError("Stock and demand must be non-negative")
    if (p.unit_cost < 0).any() or (p.reorder_point < 0).any() or (p.lead_time_days < 0).any(): raise ValueError("Cost, reorder point and lead time must be non-negative")
    if not set(f.sku_id).issubset(set(p.sku_id)): raise ValueError("Unmatched sku_id in fact data")
    if not set(f.warehouse_id).issubset(set(w.warehouse_id)): raise ValueError("Unmatched warehouse_id in fact data")

    d = f.merge(p, on="sku_id", how="left", validate="many_to_one").merge(w, on="warehouse_id", how="left", validate="many_to_one")
    if len(d) != len(f): raise ValueError("Dimension joins changed fact row count; check join keys")
    d["snapshot_date"] = pd.to_datetime(d.snapshot_date, errors="raise").dt.strftime("%Y-%m-%d")
    d["zero_or_unknown_demand"] = d.avg_daily_demand <= 0
    d["days_of_supply"] = np.where(d.avg_daily_demand > 0, d.on_hand_qty / d.avg_daily_demand, np.nan)
    d["inventory_value"] = d.on_hand_qty * d.unit_cost
    d["below_reorder_point"] = d.on_hand_qty <= d.reorder_point
    d["out_of_stock"] = d.on_hand_qty == 0
    d["stockout_risk"] = (d.avg_daily_demand > 0) & (d.days_of_supply < d.lead_time_days)
    d["risk_status"] = np.select(
        [d.out_of_stock, d.stockout_risk, d.below_reorder_point],
        ["Out of stock", "Stockout risk", "Below reorder point"], default="Healthy")
    d["priority"] = np.select(
        [d.out_of_stock, d.stockout_risk, d.below_reorder_point],
        ["P1 · Urgent review", "P1 · Urgent review", "P2 · Replenishment review"], default="P3 · Monitor")
    d["recommended_action"] = np.select(
        [d.out_of_stock & d.zero_or_unknown_demand, d.out_of_stock, d.stockout_risk, d.below_reorder_point],
        [
            "Stock is zero but demand is zero/undefined; verify demand data and open orders before estimating replenishment.",
            "Confirm open purchase orders and urgently review replenishment with the supplier.",
            "Review supplier lead time and available stock; prioritize replenishment assessment.",
            "Review reorder point, demand assumptions and upcoming replenishment cycle."
        ], default="Continue routine monitoring; reassess after the next inventory snapshot.")
    # Illustrative review quantity, not an automatic order: target lead time + explicit 7-day demo buffer.
    target_days = d.lead_time_days + SAFETY_BUFFER_DAYS
    d["illustrative_review_qty"] = np.ceil(np.maximum(0, d.avg_daily_demand * target_days - d.on_hand_qty)).astype("int64")
    d["decision_basis"] = np.select(
        [d.out_of_stock & d.zero_or_unknown_demand, d.out_of_stock, d.stockout_risk, d.below_reorder_point],
        ["No stock and demand is zero/undefined; validate demand first", "No stock on hand", "Coverage is below supplier lead time", "On-hand quantity is at/below reorder point"],
        default="No threshold crossed in this snapshot")

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "charts").mkdir(parents=True, exist_ok=True)
    n = int(len(d)); risk_count = int(d.stockout_risk.sum()); below_count = int(d.below_reorder_point.sum()); zero_count = int(d.out_of_stock.sum())
    total_units = int(d.on_hand_qty.sum()); inv_value = round(float(d.inventory_value.sum()), 2)
    snap = str(d.snapshot_date.iloc[0]) if n else "Unknown"
    kpis = [
        ["Snapshot date", snap], ["Inventory records", n], ["Unique SKUs", int(d.sku_id.nunique())],
        ["Warehouses", int(d.warehouse_id.nunique())], ["On-hand units", total_units], ["Inventory value", inv_value],
        ["Records below reorder point", below_count], ["Records at stockout risk", risk_count], ["Out-of-stock records", zero_count]
    ]
    pd.DataFrame(kpis, columns=["metric", "value"]).to_csv(output_dir / "kpi_summary.csv", index=False)
    ws = d.groupby(["warehouse_id", "warehouse_name", "region"], as_index=False).agg(
        inventory_records=("snapshot_id", "count"), on_hand_units=("on_hand_qty", "sum"), inventory_value=("inventory_value", "sum"),
        below_reorder_records=("below_reorder_point", "sum"), stockout_risk_records=("stockout_risk", "sum"),
        out_of_stock_records=("out_of_stock", "sum"))
    ws.to_csv(output_dir / "warehouse_risk_summary.csv", index=False)
    cs = d.groupby("category", as_index=False).agg(
        on_hand_units=("on_hand_qty", "sum"), inventory_value=("inventory_value", "sum"),
        stockout_risk_records=("stockout_risk", "sum"), below_reorder_records=("below_reorder_point", "sum"))
    cs.to_csv(output_dir / "category_summary.csv", index=False)
    # Decision queue: only flagged records, sorted by priority and lowest days of supply.
    queue = d[d.risk_status != "Healthy"].copy()
    queue["priority_rank"] = queue.priority.map({"P1 · Urgent review": 1, "P2 · Replenishment review": 2, "P3 · Monitor": 3})
    queue = queue.sort_values(["priority_rank", "days_of_supply", "illustrative_review_qty"], ascending=[True, True, False], na_position="first")
    queue_cols = ["snapshot_date", "priority", "risk_status", "sku_id", "product_name", "category", "warehouse_id", "warehouse_name", "region", "supplier", "on_hand_qty", "avg_daily_demand", "days_of_supply", "lead_time_days", "reorder_point", "illustrative_review_qty", "unit_cost", "inventory_value", "decision_basis", "recommended_action"]
    queue[queue_cols].to_csv(output_dir / "priority_replenishment_list.csv", index=False)
    # Additional diagnosis summary by category and region.
    diag = d.groupby(["category", "warehouse_name"], as_index=False).agg(
        records=("snapshot_id", "count"), stockout_risk_records=("stockout_risk", "sum"),
        below_reorder_records=("below_reorder_point", "sum"), on_hand_units=("on_hand_qty", "sum"), inventory_value=("inventory_value", "sum"))
    diag.to_csv(output_dir / "diagnose_category_warehouse.csv", index=False)

    # Charts are based on the current one-date snapshot; no fake time trend is shown.
    plt.figure(figsize=(9, 5)); plt.bar(ws.warehouse_name, ws.stockout_risk_records)
    plt.title("Display / Diagnose: Stockout-risk records by warehouse"); plt.xlabel("Warehouse"); plt.ylabel("SKU–warehouse records at risk")
    plt.xticks(rotation=15, ha="right"); plt.tight_layout(); plt.savefig(output_dir / "stockout_risk_by_warehouse.png", dpi=160); plt.close()
    cs2 = cs.sort_values("inventory_value", ascending=False)
    plt.figure(figsize=(9, 5)); plt.bar(cs2.category, cs2.inventory_value)
    plt.title("Display: Estimated on-hand inventory value by category"); plt.xlabel("Product category"); plt.ylabel("Synthetic currency units")
    plt.xticks(rotation=20, ha="right"); plt.tight_layout(); plt.savefig(output_dir / "inventory_value_by_category.png", dpi=160); plt.close()
    plt.figure(figsize=(9, 5)); plt.scatter(d.days_of_supply, d.lead_time_days)
    plt.xlabel("Days of supply"); plt.ylabel("Supplier lead time (days)"); plt.title("Diagnose: Stock coverage compared with lead time")
    plt.tight_layout(); plt.savefig(output_dir / "coverage_vs_lead_time.png", dpi=160); plt.close()

    p1 = int((queue.priority == "P1 · Urgent review").sum()); p2 = int((queue.priority == "P2 · Replenishment review").sum())
    topw = ws.sort_values("stockout_risk_records", ascending=False).iloc[0]
    topc = cs.sort_values("inventory_value", ascending=False).iloc[0]
    findings = [
        "DEMO FINDINGS — synthetic snapshot only", "",
        f"- {risk_count} of {n} SKU–warehouse records ({risk_count/n*100:.1f}%) have days of supply below supplier lead time.",
        f"- {below_count} of {n} records ({below_count/n*100:.1f}%) are at or below their reorder point.",
        f"- {zero_count} records are out of stock in this generated snapshot.",
        f"- {topw.warehouse_name} has the highest count of stockout-risk records ({int(topw.stockout_risk_records)}).",
        f"- {topc.category} has the largest estimated on-hand inventory value ({topc.inventory_value:,.2f} synthetic currency units).",
        f"- The decision queue contains {p1} P1 urgent-review records and {p2} P2 reorder-review records.", "",
        "These are generated sample-data findings, not actual company results. Review the action basis and validate open purchase orders before acting."
    ]
    (output_dir / "findings.txt").write_text("\n".join(findings) + "\n", encoding="utf-8")
    # JSON powers the GitHub Pages experience. Keep only a compact queue, all category/warehouse summaries.
    def clean_number(v):
        if pd.isna(v): return None
        if isinstance(v, (np.integer,)): return int(v)
        if isinstance(v, (np.floating,)): return float(v)
        return v
    records = []
    for _, row in queue.iterrows():
        rec = {k: clean_number(row[k]) for k in queue_cols}
        records.append(rec)
    all_records = []
    for _, row in d.iterrows():
        rec = {k: clean_number(row[k]) for k in queue_cols}
        all_records.append(rec)
    payload = {
        "disclosure": "Synthetic demonstration data only. One snapshot, not a trend. Suggestions are for review, not automatic orders.",
        "snapshot_date": snap,
        "source": "Generated synthetic inventory sample",
        "record_count": n,
        "unique_skus": int(d.sku_id.nunique()), "warehouses": int(d.warehouse_id.nunique()),
        "on_hand_units": total_units, "inventory_value": inv_value,
        "below_reorder_records": below_count, "stockout_risk_records": risk_count, "out_of_stock_records": zero_count,
        "stockout_risk_pct": round(risk_count/n*100,1) if n else 0,
        "below_reorder_pct": round(below_count/n*100,1) if n else 0,
        "urgent_review_records": p1, "reorder_review_records": p2,
        "safety_buffer_days_assumption": SAFETY_BUFFER_DAYS,
        "warehouse_summary": ws.to_dict(orient="records"), "category_summary": cs.to_dict(orient="records"),
        "diagnose_summary": diag.to_dict(orient="records"),
        "inventory_records": all_records,
        "action_queue": records,
        "queue_records_total": len(queue),
        "charts": {"warehouse_risk": "stockout_risk_by_warehouse.png", "category_value": "inventory_value_by_category.png", "coverage": "coverage_vs_lead_time.png"}
    }
    (output_dir / "dashboard_data.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"Analysis complete: {n} records | {risk_count} stockout-risk | {below_count} below reorder | action queue {len(queue)}")
    return payload

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", default=".", help="Folder containing the three CSV source files")
    ap.add_argument("--output-dir", default=".", help="Output folder; default keeps files in the root for GitHub Pages")
    args = ap.parse_args()
    analyze(Path(args.data_dir), Path(args.output_dir))
