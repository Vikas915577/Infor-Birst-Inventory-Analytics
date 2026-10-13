from pathlib import Path
import unittest
import pandas as pd
ROOT=Path(__file__).resolve().parent
class InventoryDataTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=pd.read_csv(ROOT/"dim_product.csv"); cls.w=pd.read_csv(ROOT/"dim_warehouse.csv"); cls.f=pd.read_csv(ROOT/"fact_inventory_snapshot.csv")
 def test_keys_unique(self):
  self.assertTrue(self.p.sku_id.is_unique); self.assertTrue(self.w.warehouse_id.is_unique); self.assertTrue(self.f.snapshot_id.is_unique)
 def test_foreign_keys_resolve(self):
  self.assertTrue(set(self.f.sku_id).issubset(set(self.p.sku_id))); self.assertTrue(set(self.f.warehouse_id).issubset(set(self.w.warehouse_id)))
 def test_quantities_nonnegative(self):
  self.assertTrue((self.f.on_hand_qty>=0).all()); self.assertTrue((self.f.avg_daily_demand>=0).all()); self.assertTrue((self.p.unit_cost>=0).all())
 def test_expected_grain(self):
  self.assertEqual(len(self.f),len(self.p)*len(self.w)); self.assertEqual(self.f.snapshot_date.nunique(),1)
if __name__=="__main__": unittest.main()
