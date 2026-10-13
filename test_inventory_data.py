from pathlib import Path
import json
import unittest
import tempfile
import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_inventory import analyze

ROOT = Path(__file__).resolve().parent

class InventoryDDDDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = pd.read_csv(ROOT / "dim_product.csv")
        cls.w = pd.read_csv(ROOT / "dim_warehouse.csv")
        cls.f = pd.read_csv(ROOT / "fact_inventory_snapshot.csv")
        cls.k = pd.read_csv(ROOT / "kpi_summary.csv")
        cls.queue = pd.read_csv(ROOT / "priority_replenishment_list.csv")
        cls.dashboard = json.loads((ROOT / "dashboard_data.json").read_text(encoding="utf-8"))

    def test_dimension_and_fact_keys_unique(self):
        self.assertTrue(self.p.sku_id.is_unique)
        self.assertTrue(self.w.warehouse_id.is_unique)
        self.assertTrue(self.f.snapshot_id.is_unique)
        self.assertFalse(self.f.duplicated(["snapshot_date", "sku_id", "warehouse_id"]).any())

    def test_foreign_keys_resolve(self):
        self.assertTrue(set(self.f.sku_id).issubset(set(self.p.sku_id)))
        self.assertTrue(set(self.f.warehouse_id).issubset(set(self.w.warehouse_id)))

    def test_nonnegative_inputs(self):
        self.assertTrue((self.f.on_hand_qty >= 0).all())
        self.assertTrue((self.f.avg_daily_demand >= 0).all())
        self.assertTrue((self.p.unit_cost >= 0).all())
        self.assertTrue((self.p.reorder_point >= 0).all())
        self.assertTrue((self.p.lead_time_days >= 0).all())

    def test_expected_fact_grain(self):
        self.assertEqual(len(self.f), len(self.p) * len(self.w))
        self.assertEqual(self.f.snapshot_date.nunique(), 1)

    def test_all_rows_and_queue_count_reconcile(self):
        self.assertEqual(len(self.dashboard["inventory_records"]), len(self.f))
        self.assertEqual(self.dashboard["record_count"], len(self.f))
        self.assertEqual(len(self.dashboard["action_queue"]), len(self.queue))
        self.assertEqual(self.dashboard["queue_records_total"], len(self.queue))
        self.assertTrue(all(row["risk_status"] != "Healthy" for row in self.dashboard["action_queue"]))
        self.assertEqual(sum(row["risk_status"] != "Healthy" for row in self.dashboard["inventory_records"]), len(self.queue))

    def test_dashboard_metrics_reconcile(self):
        self.assertEqual(self.dashboard["on_hand_units"], int(self.f.on_hand_qty.sum()))
        self.assertEqual(self.dashboard["unique_skus"], self.p.sku_id.nunique())
        self.assertEqual(self.dashboard["warehouses"], self.w.warehouse_id.nunique())
        self.assertAlmostEqual(self.dashboard["inventory_value"], (self.f.merge(self.p, on="sku_id").eval("on_hand_qty * unit_cost").sum()), places=2)
        self.assertEqual(self.dashboard["stockout_risk_records"], sum(row["risk_status"] == "Stockout risk" for row in self.dashboard["inventory_records"]))
        self.assertEqual(self.dashboard["below_reorder_records"], sum(row["on_hand_qty"] <= row["reorder_point"] for row in self.dashboard["inventory_records"]))

    def test_decision_queue_contains_only_flagged_records(self):
        allowed = {"Out of stock", "Stockout risk", "Below reorder point"}
        self.assertTrue(set(self.queue.risk_status).issubset(allowed))
        self.assertTrue((self.queue.illustrative_review_qty >= 0).all())
        self.assertTrue(self.queue.recommended_action.notna().all())
        self.assertTrue(self.queue.decision_basis.notna().all())

    def test_review_quantity_uses_declared_assumption(self):
        queue = self.queue.merge(self.p[["sku_id", "lead_time_days"]], on="sku_id", suffixes=("", "_product"))
        expected = (queue.avg_daily_demand * (queue.lead_time_days + self.dashboard["safety_buffer_days_assumption"]) - queue.on_hand_qty).clip(lower=0).apply(lambda x: int(-(-x // 1)))
        self.assertTrue((expected.astype(int).values == queue.illustrative_review_qty.astype(int).values).all())

    def test_queue_sorted_priority_then_coverage(self):
        rank = self.queue.priority.map({"P1 · Urgent review": 1, "P2 · Replenishment review": 2, "P3 · Monitor": 3})
        self.assertTrue(rank.is_monotonic_increasing)

    def test_zero_demand_is_undefined_and_requires_review(self):
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            source = temp_root / "source"
            output = temp_root / "output"
            source.mkdir()
            product = self.p.iloc[[0]].copy()
            warehouse = self.w.iloc[[0]].copy()
            fact = self.f[(self.f.sku_id == product.iloc[0].sku_id) & (self.f.warehouse_id == warehouse.iloc[0].warehouse_id)].iloc[[0]].copy()
            fact.loc[:, "on_hand_qty"] = 0
            fact.loc[:, "avg_daily_demand"] = 0
            product.to_csv(source / "dim_product.csv", index=False)
            warehouse.to_csv(source / "dim_warehouse.csv", index=False)
            fact.to_csv(source / "fact_inventory_snapshot.csv", index=False)
            payload = analyze(source, output)
            row = payload["inventory_records"][0]
            self.assertIsNone(row["days_of_supply"])
            self.assertEqual(row["risk_status"], "Out of stock")
            self.assertIn("demand is zero/undefined", row["recommended_action"])
            self.assertIn("validate demand first", row["decision_basis"])
            self.assertEqual(row["illustrative_review_qty"], 0)

    def test_required_dashboard_files_exist(self):
        for name in ["index.html", "dashboard_data.json", "BIRST_MODEL_AND_DASHBOARD_GUIDE.md", "DDD_USER_STORY_AND_ACCEPTANCE_CRITERIA.md", "RESEARCH_REFERENCES.md", "UPLOAD_FIX_GUIDE.md"]:
            self.assertTrue((ROOT / name).exists(), name)
        for name in ["stockout_risk_by_warehouse.png", "inventory_value_by_category.png", "coverage_vs_lead_time.png"]:
            self.assertTrue((ROOT / name).exists(), name)

if __name__ == "__main__":
    unittest.main(verbosity=2)
