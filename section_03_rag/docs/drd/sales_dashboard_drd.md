# Sales Dashboard DRD

The Sales Dashboard is used by regional managers to track weekly revenue against target.
The primary KPI is net_revenue, defined as the sum of order_total for orders where order_status is not CANCELLED.
Dashboard data refreshes every morning at 07:00 UTC after the orders load completes.
Managers may filter by region, product category and customer_segment.
Access is restricted by region, so a manager only sees rows for the region assigned in the access matrix.
Dashboard load time must stay under 5 seconds for the default view.
