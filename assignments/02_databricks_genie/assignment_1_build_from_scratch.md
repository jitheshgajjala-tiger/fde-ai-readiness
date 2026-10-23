# Assignment 1: Build from scratch

**Section:** 2. Databricks Genie (Conversational Analytics)

Create a Genie Space over a real Gold table set for one business domain (e.g., order fulfillment). Add table/column descriptions and at least 3 sample instructions covering common business terms.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (live Genie API output recorded below)
- [x] Result and what I learned

## Approach

Built the order-fulfilment Genie space over the seeded Unity Catalog tables `workspace.fde_prep.fact_orders`, `dim_customer`, and `dim_product`. The workspace API reported the space title as **Sales Orders and Customer Data**, using warehouse `ce72158123970c93`. The prep guide defines the table/column comments, customer/product joins, and business terms for revenue, on-time delivery, and late delivery.

Tested natural-language questions through the Genie API and inspected its generated SQL and result rows.

## Evidence

| Question | Generated SQL behavior | Genie result |
|---|---|---|
| How many orders are there? | `COUNT(*)` from `fact_orders` | 24 |
| How many orders were cancelled? | `COUNT(*)` filtered to `order_status = 'CANCELLED'` | 2 |
| What is our on-time delivery rate? | Delivered rows with dates; compares `delivered_date <= promised_date` | 70.5882% (70.6% rounded) |
| Show net revenue by region. | Joins `fact_orders` to `dim_product`; sums `quantity * unit_price`; excludes cancelled | South 1,725; East 1,515; West 1,360; North 1,250 |
| Show delivered orders by region. | Counts rows filtered to `order_status = 'DELIVERED'` | East 5; North 4; South 4; West 4 |

## Result and what I learned

- Genie interpreted the seeded table and column metadata well enough to generate SQL for counts, a date-based delivery metric, and revenue requiring a product join.
- The on-time answer used rows with both delivery and promised dates and returned 70.5882%, consistent with the expected 70.6% rounded.
- The test confirms query behavior for these prompts; it does not independently inspect every description or every instruction in the space. Capture the space configuration screenshot if the reviewer requires proof of metadata and instruction setup.

## Notes

The Genie title returned by the workspace API is `Sales Orders and Customer Data`; use that displayed name if it differs from a local label.

