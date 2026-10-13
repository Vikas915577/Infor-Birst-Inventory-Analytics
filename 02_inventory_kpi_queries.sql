-- PostgreSQL queries for Inventory & Stock Risk Analytics
-- KPI totals
SELECT f.snapshot_date, COUNT(*) AS sku_warehouse_records, COUNT(DISTINCT f.sku_id) AS unique_skus, COUNT(DISTINCT f.warehouse_id) AS warehouses, SUM(f.on_hand_qty) AS on_hand_units, ROUND(SUM(f.on_hand_qty*p.unit_cost),2) AS inventory_value, SUM(CASE WHEN f.on_hand_qty<=p.reorder_point THEN 1 ELSE 0 END) AS below_reorder_records, SUM(CASE WHEN f.avg_daily_demand>0 AND f.on_hand_qty/f.avg_daily_demand<p.lead_time_days THEN 1 ELSE 0 END) AS stockout_risk_records FROM fact_inventory_snapshot f JOIN dim_product p USING(sku_id) GROUP BY f.snapshot_date;
-- Risk by warehouse
SELECT w.warehouse_name,w.region,COUNT(*) AS records,SUM(CASE WHEN f.on_hand_qty<=p.reorder_point THEN 1 ELSE 0 END) AS below_reorder_records,SUM(CASE WHEN f.avg_daily_demand>0 AND f.on_hand_qty/f.avg_daily_demand<p.lead_time_days THEN 1 ELSE 0 END) AS stockout_risk_records,SUM(f.on_hand_qty) AS on_hand_units,ROUND(SUM(f.on_hand_qty*p.unit_cost),2) AS inventory_value FROM fact_inventory_snapshot f JOIN dim_product p USING(sku_id) JOIN dim_warehouse w USING(warehouse_id) GROUP BY w.warehouse_name,w.region ORDER BY stockout_risk_records DESC;
-- Priority list
SELECT f.snapshot_date,f.sku_id,p.product_name,p.category,w.warehouse_name,f.on_hand_qty,f.avg_daily_demand,ROUND(f.on_hand_qty::NUMERIC/NULLIF(f.avg_daily_demand,0),1) AS days_of_supply,p.reorder_point,p.lead_time_days,CASE WHEN f.on_hand_qty=0 THEN 'Out of stock' WHEN f.avg_daily_demand>0 AND f.on_hand_qty::NUMERIC/f.avg_daily_demand<p.lead_time_days THEN 'Stockout risk' WHEN f.on_hand_qty<=p.reorder_point THEN 'Below reorder point' ELSE 'Healthy' END AS risk_status,ROUND(f.on_hand_qty*p.unit_cost,2) AS inventory_value,p.supplier FROM fact_inventory_snapshot f JOIN dim_product p USING(sku_id) JOIN dim_warehouse w USING(warehouse_id) WHERE f.on_hand_qty<=p.reorder_point OR (f.avg_daily_demand>0 AND f.on_hand_qty::NUMERIC/f.avg_daily_demand<p.lead_time_days) ORDER BY CASE WHEN f.on_hand_qty=0 THEN 0 ELSE 1 END,(f.on_hand_qty::NUMERIC/NULLIF(f.avg_daily_demand,0)) ASC NULLS FIRST;
-- Inventory value by category
SELECT p.category,SUM(f.on_hand_qty) AS on_hand_units,ROUND(SUM(f.on_hand_qty*p.unit_cost),2) AS inventory_value,SUM(CASE WHEN f.on_hand_qty<=p.reorder_point THEN 1 ELSE 0 END) AS below_reorder_records FROM fact_inventory_snapshot f JOIN dim_product p USING(sku_id) GROUP BY p.category ORDER BY inventory_value DESC;


-- Q6: DDD decision queue. A transparent 7-day buffer is a demo assumption, not a purchase order.
-- Review every recommendation against open POs, MOQ/pack size, current forecast, budget and supplier constraints.
SELECT f.snapshot_date, p.sku_id, p.product_name, p.category, w.warehouse_name,
       f.on_hand_qty, f.avg_daily_demand,
       ROUND(f.on_hand_qty::NUMERIC / NULLIF(f.avg_daily_demand,0), 1) AS days_of_supply,
       p.lead_time_days, p.reorder_point,
       CASE
         WHEN f.on_hand_qty = 0 THEN 'P1 - Urgent review'
         WHEN f.avg_daily_demand > 0 AND f.on_hand_qty::NUMERIC / f.avg_daily_demand < p.lead_time_days THEN 'P1 - Urgent review'
         WHEN f.on_hand_qty <= p.reorder_point THEN 'P2 - Replenishment review'
         ELSE 'P3 - Monitor'
       END AS decision_priority,
       GREATEST(0, CEIL(f.avg_daily_demand * (p.lead_time_days + 7) - f.on_hand_qty))::INTEGER AS illustrative_review_qty,
       CASE
         WHEN f.on_hand_qty = 0 THEN 'Confirm open PO and urgently review replenishment.'
         WHEN f.avg_daily_demand > 0 AND f.on_hand_qty::NUMERIC / f.avg_daily_demand < p.lead_time_days THEN 'Review stock cover and supplier lead time; prioritize replenishment assessment.'
         WHEN f.on_hand_qty <= p.reorder_point THEN 'Review reorder trigger and next replenishment cycle.'
         ELSE 'Monitor on next snapshot.'
       END AS recommended_action
FROM fact_inventory_snapshot f
JOIN dim_product p USING (sku_id)
JOIN dim_warehouse w USING (warehouse_id)
WHERE f.on_hand_qty = 0
   OR (f.avg_daily_demand > 0 AND f.on_hand_qty::NUMERIC / f.avg_daily_demand < p.lead_time_days)
   OR f.on_hand_qty <= p.reorder_point
ORDER BY CASE WHEN f.on_hand_qty = 0 THEN 1 WHEN f.avg_daily_demand > 0 AND f.on_hand_qty::NUMERIC / f.avg_daily_demand < p.lead_time_days THEN 2 ELSE 3 END,
         f.on_hand_qty::NUMERIC / NULLIF(f.avg_daily_demand,0) ASC NULLS FIRST;
