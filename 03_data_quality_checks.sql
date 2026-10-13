-- Additional data-quality checks (PostgreSQL)
SELECT * FROM fact_inventory_snapshot WHERE on_hand_qty<0 OR avg_daily_demand<0;
SELECT * FROM dim_product WHERE unit_cost IS NULL OR unit_cost<0 OR reorder_point IS NULL OR reorder_point<0 OR lead_time_days IS NULL OR lead_time_days<0;
SELECT w.warehouse_name,COUNT(f.snapshot_id) AS record_count FROM dim_warehouse w LEFT JOIN fact_inventory_snapshot f USING(warehouse_id) GROUP BY w.warehouse_name ORDER BY w.warehouse_name;
