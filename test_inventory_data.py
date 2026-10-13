from pathlib import Path
import json, unittest
import pandas as pd
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

    def test_foreign_keys_resolve(self):
        self.assertTrue(set(self.f.sku_id).issubset(set(self.p.sku_id)))
        self.assertTrue(set(self.f.warehouse_id).issubset(set(self.w.warehouse_id)))

    def test_nonnegative_inputs(self):
        self.assertTrue((self.f.on_hand_qty >= 0).all())
        self.assertTrue((self.f.avg_daily_demand >= 0).all())
        self.assertTrue((self.p.unit_cost >= 0).all())

    def test_expected_fact_grain(self):
        self.assertEqual(len(self.f), len(self.p) * len(self.w))
        self.assertEqual(self.f.snapshot_date.nunique(), 1)

    def test_decision_queue_contains_only_flagged_records(self):
        self.assertTrue(set(self.queue.risk_status).issubset({"Out of stock", "Stockout risk", "Below reorder point"}))
        self.assertTrue((self.queue.illustrative_review_qty >= 0).all())
        self.assertTrue(self.queue.recommended_action.notna().all())

    def test_dashboard_metrics_reconcile(self):
        self.assertEqual(self.dashboard["record_count"], len(self.f))
        self.assertEqual(self.dashboard["on_hand_units"], int(self.f.on_hand_qty.sum()))
        self.assertEqual(self.dashboard["unique_skus"], self.p.sku_id.nunique())
        self.assertEqual(self.dashboard["queue_records_total"], len(self.queue))

if __name__ == "__main__": unittest.main()
