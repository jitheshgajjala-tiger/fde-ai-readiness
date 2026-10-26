# Genie space setup (Section 2)

Use the tables created by `notebooks/02_seed_gold_tables.py`. Business domain: order fulfilment.

## Assignment 1: build the space
1. Databricks: Genie, New. Add only these three tables (not the whole schema): `dim_customer`, `dim_product`, `fact_orders`.
2. Check that every table and column shows the comment from the seed notebook. If not, re-run the seed notebook.
3. Add this **general instruction** (single text instruction):
   > Revenue is quantity multiplied by the product unit_price from dim_product, and excludes orders with order_status CANCELLED.
   > "On-time delivery" means delivered_date is on or before promised_date, counted over DELIVERED orders only.
   > "Late" means delivered_date is after promised_date. Round percentages to one decimal place.
4. Add a **join**: `fact_orders.product_id = dim_product.product_id` (many to one) and `fact_orders.customer_id = dim_customer.customer_id` (many to one).
5. Add these tested **example SQL** queries (run each once in the space first):

**On-time delivery rate**
```sql
SELECT ROUND(100.0 * SUM(CASE WHEN delivered_date <= promised_date THEN 1 ELSE 0 END) / COUNT(*), 1) AS on_time_pct
FROM fact_orders
WHERE order_status = 'DELIVERED'
```

**Net revenue by region**
```sql
SELECT o.region, SUM(o.quantity * p.unit_price) AS net_revenue
FROM fact_orders o JOIN dim_product p ON o.product_id = p.product_id
WHERE o.order_status <> 'CANCELLED'
GROUP BY o.region
ORDER BY net_revenue DESC
```

**Late orders**
```sql
SELECT order_id, region, datediff(delivered_date, promised_date) AS days_late
FROM fact_orders
WHERE order_status = 'DELIVERED' AND delivered_date > promised_date
ORDER BY days_late DESC
```

6. Save the space and copy its id from the URL into `GENIE_SPACE_ID` in `00_config`.

Known answers to check the space against: 24 orders, 2 cancelled, 17 delivered, 5 late, on-time rate 70.6 percent.

## Assignment 2: break and fix
1. **Before** adding the on-time instruction and example, ask: *What is our on-time rate?*
   The word has two reasonable meanings: delivered by the promised date (70.6 percent) or shipped within 2 days of ordering (76.5 percent).
2. Record which one Genie picked and the SQL it generated.
3. Fix it in the **space**, not the question: add the general instruction and the "On-time delivery rate" example SQL above.
4. Ask the same question again and confirm the answer is now 70.6 percent.

## Assignment 3: governance
Run `notebooks/03_genie_governance.py` with a second user.

## Assignment 4: programmatic access
Run `notebooks/04_genie_api.py`.

## Assignment 5: business handoff
Stakeholder ask: "show me how markets are performing". Timebox 60 minutes. Record: which tables you included and excluded and why,
how you interpreted "markets" (region), how you interpreted "performing" (net revenue and on-time rate), and three sample questions.
