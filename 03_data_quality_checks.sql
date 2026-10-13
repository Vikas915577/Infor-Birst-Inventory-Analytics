-- Data quality and reconciliation checks. Expected to return no rows for duplicate grain / broken foreign keys.
SELECT snapshot_date,sku_id,warehouse_id,COUNT(*) AS duplicate_count FROM fact_inventory_snapshot GROUP BY snapshot_date,sku_id,warehouse_id HAVING COUNT(*)>1;
SELECT f.* FROM fact_inventory_snapshot f LEFT JOIN dim_product p USING(sku_id) LEFT JOIN dim_warehouse w USING(warehouse_id) WHERE p.sku_id IS NULL OR w.warehouse_id IS NULL;
SELECT * FROM fact_inventory_snapshot WHERE on_hand_qty<0 OR avg_daily_demand<0;
SELECT warehouse_id,COUNT(*) AS record_count FROM fact_inventory_snapshot GROUP BY warehouse_id ORDER BY warehouse_id;
