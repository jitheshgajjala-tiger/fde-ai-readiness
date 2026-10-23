# Assignment 2: Break and fix

**Section:** 2. Databricks Genie (Conversational Analytics)

Deliberately ask Genie an ambiguous question likely to produce a wrong answer (e.g., a metric with two possible definitions). Diagnose the root cause and fix it by improving metadata/instructions — not by rewording the question.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (post-fix live Genie output recorded below)
- [x] Result and what I learned
- [x] Capture the ambiguous answer and generated SQL before adding the definition, then repeat the identical question after the fix
- [x] Confirm the temporary incorrect instruction has been removed from the duplicate Genie space

## Approach

Used the ambiguous question **“What is our on-time delivery rate?”** and checked the generated SQL and result from the live Genie API. The intended definition is delivered orders whose `delivered_date` is on or before `promised_date`, divided by delivered orders with both dates present.

## Evidence

### Before correction: alternate definition

In the duplicate space, the temporary instruction defined on-time as shipping within two calendar days after order date. Genie returned:

```text
On-Time Delivery Rate
Our on-time delivery rate is 76.47% — 13 of 17 delivered orders were shipped within two calendar days of the order date.
```

This is the deliberately different measure (ship-date speed), not the intended delivery-promise measure. The downloaded profile `query-profile_01f1ce77-9614-149b-8632-984bac7509d4.json` reports `FINISHED`, no error, one result row, and shows this SQL:

```sql
SELECT
	COUNT(*) AS delivered_orders,
	SUM(CASE WHEN DATEDIFF(ship_date, order_date) <= 2 THEN 1 ELSE 0 END) AS on_time_orders,
	ROUND(100.0 * SUM(CASE WHEN DATEDIFF(ship_date, order_date) <= 2 THEN 1 ELSE 0 END) / COUNT(*), 2) AS on_time_rate_pct
FROM workspace.fde_prep.fact_orders
WHERE order_status = 'DELIVERED'
```

### After correction: intended definition

After replacing the temporary instruction with the delivered-versus-promised-date definition, the same question returned:

```text
On-Time Delivery Rate
Our on-time delivery rate is 70.6% (12 of 17 delivered orders arrived on or before their promised date).
This is calculated across orders with status DELIVERED that have both a delivered date and a promised date recorded.
```

The corrected definition is delivered orders whose `delivered_date <= promised_date`, divided by delivered orders with both dates present. The generated SQL for the corrected answer is:

```sql
SELECT
  COUNT(*) AS delivered_orders_with_dates,
  SUM(CASE WHEN delivered_date <= promised_date THEN 1 ELSE 0 END) AS on_time_orders,
  ROUND(SUM(CASE WHEN delivered_date <= promised_date THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS on_time_rate_pct
FROM workspace.fde_prep.fact_orders
WHERE order_status = 'DELIVERED'
  AND delivered_date IS NOT NULL
  AND promised_date IS NOT NULL
```

The downloaded profile `query-profile_01f1ce77-f02c-1643-bcc6-747fff1c372b.json` reports `FINISHED`, no error, and one result row. Returned result: `delivered_orders_with_dates = 17`, `on_time_orders = 12`, `on_time_rate_pct = 70.59`. This matches Genie’s displayed answer of `70.6%` after rounding to one decimal place.

## Result and what I learned

- The temporary alternate definition produced 76.47% (13/17) based on shipping within two days of order date.
- The intended delivery-promise definition produced 70.59% (12/17) based on `delivered_date <= promised_date`.
- This demonstrates how the business definition changes the metric while the question can remain “What is our on-time delivery rate?”.
- The query profiles show the alternate ship-date query ran first and the intended promised-date query ran afterward. The temporary incorrect instruction was removed from the duplicate Genie space; the original space was not changed for this test.

## Notes

The distinction matters: “on-time” could refer to delivery versus promise date or shipping versus a warehouse SLA. Keep the correction in Genie instructions/example SQL, not in a rephrased question. The downloaded profile JSON files contain workspace/user metadata; keep originals private and do not commit them. The SQL and summarized results above are the shareable evidence.

