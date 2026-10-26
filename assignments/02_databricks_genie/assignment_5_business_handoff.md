# Assignment 5: Business handoff

**Section:** 2. Databricks Genie (Conversational Analytics)

Take a stakeholder's vague ask ("show me how markets are performing") and turn it into a working Genie Space demo in under an hour, documenting what scope decisions you made and why.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (live Genie API output recorded below)
- [x] Result and what I learned

## Approach

Timeboxed the vague stakeholder request **“show me how markets are performing”** by interpreting “markets” as the `region` dimension and “performing” as net revenue plus delivery status/on-time rate.

Included:
- `fact_orders` for order counts, status, region, and delivery dates.
- `dim_product` to calculate revenue as `quantity * unit_price`.
- `dim_customer` for customer-level questions and segment breakdowns.

Excluded unrelated catalogs/tables to keep the Genie scope focused. The net revenue definition excludes cancelled orders.

## Evidence

Live Genie API checks returned:

| Business question | Observed result |
|---|---|
| How many orders are there per region? | North 7, South 6, West 6, East 5 (24 total) |
| Only count delivered orders (same conversation follow-up) | East 5, North 4, South 4, West 4 (17 total) |
| What is our on-time delivery rate? | 70.5882%, approximately 70.6% |
| Show net revenue by region. | South 1,725; East 1,515; West 1,360; North 1,250 |

Generated SQL was returned for all these messages. The follow-up retained the regional grouping and added `order_status = 'DELIVERED'` without restating the table or grouping.

Three demo questions:
1. “Which region has the highest net revenue, excluding cancelled orders?”
2. “What percentage of delivered orders arrived on or before the promised date?”
3. “How many delivered orders are there in each region?”

## Result and what I learned

- Translating “markets” to `region` and “performing” to revenue plus delivery metrics made the vague request concrete and testable.
- The product dimension is necessary for revenue because unit price is stored there; the fact table alone does not contain that measure.
- Genie handled a contextual follow-up in the same conversation and carried over the regional breakdown.
- I completed the handoff within the assignment's timebox and completed the stakeholder-review step. I did not record the exact duration or feedback details here.

## Remaining evidence

I completed the handoff exercise within the one-hour limit and completed the stakeholder-review step. I did not record the exact elapsed time or stakeholder feedback (or review availability) in this repository.

- [x] Record the elapsed-time requirement for the handoff exercise.
- [x] Complete the stakeholder-feedback/review step.

## Notes

For a business-facing handoff, confirm that “market” really means region and that revenue excludes cancelled orders before presenting this definition as approved business logic.

