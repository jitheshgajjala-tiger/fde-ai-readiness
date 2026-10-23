# Assignment 4: Programmatic access

**Section:** 2. Databricks Genie (Conversational Analytics)

Use the Genie API to start a conversation, ask a follow-up question in the same thread, and extract the generated SQL — without touching the UI.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (API output recorded below)
- [x] Result and what I learned

## Approach

Used the Genie Chat-mode REST API through the Databricks workspace client, without using the Genie UI:

1. Started a conversation with `How many orders are there per region?`.
2. Waited until the message status was `COMPLETED`.
3. Extracted the generated SQL and query result rows.
4. Sent `Only count delivered orders.` as a follow-up in the same conversation, then extracted its SQL and rows.

## Evidence

First message:

```text
status: COMPLETED
SQL:
SELECT region, COUNT(*) AS order_count
FROM workspace.fde_prep.fact_orders
WHERE region IS NOT NULL
GROUP BY region
ORDER BY order_count DESC, region ASC
rows: North=7, South=6, West=6, East=5
```

Follow-up message:

```text
status: COMPLETED
SQL:
SELECT region, COUNT(*) AS delivered_order_count
FROM workspace.fde_prep.fact_orders
WHERE order_status = 'DELIVERED' AND region IS NOT NULL
GROUP BY region
ORDER BY delivered_order_count DESC, region ASC
rows: East=5, North=4, South=4, West=4
```

## Result and what I learned

- Both API messages completed successfully, and the first message's generated SQL and result rows were retrieved programmatically.
- The follow-up reused the conversation context: it retained the region breakdown and added `order_status = 'DELIVERED'` even though the follow-up only said "Only count delivered orders."
- The counts are consistent with the seed data: 24 total orders across regions and 17 delivered orders across regions.
- The API flow can support a programmatic consumer without using the Genie UI. The test covered one conversation and one follow-up; it is not a reliability or concurrency test.

## Notes

Remove test conversations when no longer needed using the Genie conversation delete endpoint. Do not record access tokens in this assignment.

