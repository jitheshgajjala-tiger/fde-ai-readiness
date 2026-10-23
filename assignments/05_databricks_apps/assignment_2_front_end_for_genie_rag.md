# Assignment 2: Front-end for Genie/RAG

**Section:** 5. Databricks Apps

Build a small app UI that lets a user type a question and displays the answer from either a Genie conversation (Section 2) or a RAG pipeline (Section 3).

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (live Genie responses and generated SQL recorded below)
- [x] Result and what I learned

## Notes

The app's **Ask Genie** tab calls the Genie conversation API using the `genie-space` App resource mapped to `GENIE_SPACE_ID`. The resource is configured for the existing Sales Orders and Customer Data Genie Agent. Live questions were sent from the deployed app as the app service principal.

## Evidence

Question: `How many orders were cancelled?`

```text
There were 2 cancelled orders (cancelled_orders = 2).
```

Generated SQL:

```sql
SELECT COUNT(*) AS cancelled_orders
FROM workspace.fde_prep.fact_orders
WHERE order_status = 'CANCELLED'
```

Question: `What is the total revenue by region, excluding cancelled orders?`

Observed result: East 1,515; North 1,250; South 1,725; West 1,360. South is highest among the four regions.

Generated SQL:

```sql
SELECT
	f.region AS region,
	SUM(f.quantity * p.unit_price) AS total_revenue
FROM workspace.fde_prep.fact_orders AS f
INNER JOIN workspace.fde_prep.dim_product AS p
	ON f.product_id = p.product_id
WHERE f.order_status <> 'CANCELLED'
	AND f.region IS NOT NULL
GROUP BY f.region
ORDER BY f.region
```

## Result and what I learned

- The deployed app successfully submitted questions to Genie and displayed both natural-language answers and generated SQL.
- The cancelled-order count (2) and regional revenue totals match the seeded workspace results.
- The initial display exposed Markdown markers literally. The app now renders Genie responses as Markdown and formats generated SQL in a fenced SQL block; redeploy this presentation fix to confirm the polished display.

