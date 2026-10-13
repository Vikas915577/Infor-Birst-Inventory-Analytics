#!/usr/bin/env python3
"""Analyze synthetic inventory snapshots and write KPIs and charts."""
from pathlib import Path
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data-dir',default='data/source_synthetic')
    ap.add_argument('--output-dir',default='outputs')
    a=ap.parse_args(); src=Path(a.data_dir); out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True); (out/'charts').mkdir(exist_ok=True)
    p=pd.read_csv(src/'dim_product.csv'); w=pd.read_csv(src/'dim_warehouse.csv'); f=pd.read_csv(src/'fact_inventory_snapshot.csv')
    d=f.merge(p,on='sku_id',validate='many_to_one').merge(w,on='warehouse_id',validate='many_to_one')
    if d.snapshot_id.isna().any() or d.snapshot_id.duplicated().any(): raise ValueError('snapshot_id must be populated and unique')
    if (d.on_hand_qty<0).any() or (d.avg_daily_demand<0).any(): raise ValueError('Negative stock/demand found')
    d['days_of_supply']=np.where(d.avg_daily_demand>0,d.on_hand_qty/d.avg_daily_demand,np.nan)
    d['inventory_value']=d.on_hand_qty*d.unit_cost; d['below_reorder_point']=d.on_hand_qty<=d.reorder_point; d['stockout_risk']=d.days_of_supply<d.lead_time_days
    d['risk_status']=np.select([d.on_hand_qty==0,d.stockout_risk,d.below_reorder_point],['Out of stock','Stockout risk','Below reorder point'],default='Healthy')
    pd.DataFrame([['Snapshot date',str(d.snapshot_date.iloc[0])],['Inventory records',len(d)],['Unique SKUs',d.sku_id.nunique()],['Warehouses',d.warehouse_id.nunique()],['On-hand units',int(d.on_hand_qty.sum())],['Inventory value',round(float(d.inventory_value.sum()),2)],['Records below reorder point',int(d.below_reorder_point.sum())],['Records at stockout risk',int(d.stockout_risk.sum())],['Out-of-stock records',int((d.on_hand_qty==0).sum())]],columns=['metric','value']).to_csv(out/'kpi_summary.csv',index=False)
    ws=d.groupby(['warehouse_id','warehouse_name','region'],as_index=False).agg(inventory_records=('snapshot_id','count'),on_hand_units=('on_hand_qty','sum'),inventory_value=('inventory_value','sum'),below_reorder_records=('below_reorder_point','sum'),stockout_risk_records=('stockout_risk','sum'),out_of_stock_records=('on_hand_qty',lambda s:int((s==0).sum())))
    ws.to_csv(out/'warehouse_risk_summary.csv',index=False)
    cs=d.groupby('category',as_index=False).agg(on_hand_units=('on_hand_qty','sum'),inventory_value=('inventory_value','sum'),stockout_risk_records=('stockout_risk','sum'),below_reorder_records=('below_reorder_point','sum')); cs.to_csv(out/'category_summary.csv',index=False)
    risk=d[d.stockout_risk|d.below_reorder_point].sort_values(['stockout_risk','days_of_supply'],ascending=[False,True]); risk[['snapshot_date','sku_id','product_name','category','warehouse_id','warehouse_name','on_hand_qty','avg_daily_demand','days_of_supply','reorder_point','lead_time_days','unit_cost','inventory_value','risk_status','supplier']].to_csv(out/'priority_replenishment_list.csv',index=False)
    plt.figure(figsize=(9,5)); plt.bar(ws.warehouse_name,ws.stockout_risk_records); plt.title('Inventory Records at Stockout Risk by Warehouse'); plt.xlabel('Warehouse'); plt.ylabel('Records at risk'); plt.xticks(rotation=15,ha='right'); plt.tight_layout(); plt.savefig(out/'charts/stockout_risk_by_warehouse.png',dpi=150); plt.close()
    csort=cs.sort_values('inventory_value',ascending=False); plt.figure(figsize=(9,5)); plt.bar(csort.category,csort.inventory_value); plt.title('Inventory Value by Product Category'); plt.xlabel('Category'); plt.ylabel('Inventory value (currency units)'); plt.xticks(rotation=20,ha='right'); plt.tight_layout(); plt.savefig(out/'charts/inventory_value_by_category.png',dpi=150); plt.close()
    plt.figure(figsize=(9,5)); plt.scatter(d.days_of_supply,d.lead_time_days); plt.title('Stock Coverage vs Supplier Lead Time'); plt.xlabel('Days of supply'); plt.ylabel('Supplier lead time (days)'); plt.tight_layout(); plt.savefig(out/'charts/coverage_vs_lead_time.png',dpi=150); plt.close()
    topw=ws.sort_values('stockout_risk_records',ascending=False).iloc[0]; topc=cs.sort_values('inventory_value',ascending=False).iloc[0]; n=len(d); rc=int(d.stockout_risk.sum()); br=int(d.below_reorder_point.sum())
    (out/'findings.txt').write_text('DEMO FINDINGS — synthetic dataset only\n\n'+f'- {rc} of {n} records ({rc/n*100:.1f}%) have days of supply below lead time.\n'+f'- {br} of {n} records ({br/n*100:.1f}%) are at/below reorder point.\n'+f'- {topw.warehouse_name} has highest stockout-risk record count ({int(topw.stockout_risk_records)}).\n'+f'- {topc.category} has largest inventory value ({topc.inventory_value:,.2f} currency units).\n',encoding='utf-8')
    print('Analysis complete:',out.resolve())
if __name__=='__main__': main()
