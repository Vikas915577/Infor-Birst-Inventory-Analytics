# Research References & How They Inform This Project

This list separates official product capability documentation from the dashboard-design framework.

## Official Infor Birst documentation
1. **Creating dashboards** — https://docs.infor.com/birst/latest/en-us/birstolh/dashboards_user/ifj1655271234451.html
   - Supports report dashlets from Visualizer/Designer, prompt filters, KPI dashlets, drill-across, text boxes, and publish/test workflows.
2. **KPI dashlets** — https://docs.infor.com/birst/latest/en-us/birstolh/dashboards_user/jmt1655271239123.html
   - Supports selecting a measure, title, indicator, chart, format and layout for a KPI dashlet.
3. **Dashboard filters** — https://docs.infor.com/birst/2026.10/en-us/birstolh/dashboards_user/ieb1655271241138.html
   - Supports filtering into different levels of detail and date/range subsets.
4. **Visualizer filters** — https://docs.infor.com/birst/2025.x/en-us/birstolh/reports_user/xah1655271135431.html
   - Describes applying attribute/measure filters while building reports.
5. **Subject areas** — https://docs.infor.com/birst/latest/en-us/birstolh/reports_user/bha1655271152572.html
   - Describes user-facing attributes/measures and recommends custom subject areas with relevant fields and user-friendly labels.
6. **Infor Analytics with Birst** — https://developer.infor.com/tutorials/analytics-with-birst
   - Overview of reports, dashboards, semantic layer and analytics use.

## Display → Diagnose → Decide
Infor’s value-based design / smart embedded analytics white paper describes a guided information architecture **Display > Diagnose > Decide**. A public copy is listed here:
https://dam.infor.com/api/public/content/12f4f63a51784e6d9c0046b63385c2fd?v=b0eacc16

Applied here as:
- **Display:** show whether there is a meaningful inventory signal.
- **Diagnose:** locate which warehouse/category/SKU triggered it and why.
- **Decide:** present a prioritized review queue, owner-facing next step and explicitly stated assumptions.

## Product design decisions inferred for this portfolio
The exact inventory thresholds and 7-day safety buffer are not prescribed by Infor; they are transparent synthetic-demo assumptions. A real organization must replace them with approved inventory policy and reconcile against its source of truth.
