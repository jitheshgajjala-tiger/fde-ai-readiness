# Assignment 5: Query tuning

**Section:** 4. Vector Database Creation in Databricks

Compare results for the same query at `top_k=3` vs. `top_k=15`, and describe how you'd choose `top_k` for a real RAG use case based on what you saw.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (notebook output recorded below)
- [x] Result and what I learned

## Approach

Ran the same query, `What happens to rows with a null key?`, against the Delta Sync index with `num_results=3` and `num_results=15`. Scores are returned by the index; the list is sorted highest to lowest.

## Evidence

**Top 3:**

| Rank | Chunk | Score |
|---|---|---:|
| 1 | `dq_rules.md#2` | 0.4884 |
| 2 | `orders_sttm.md#1` | 0.4755 |
| 3 | `dq_rules.md#1` | 0.4749 |

**Top 15:** the same three top-ranked chunks, followed by 12 more chunks. The last two returned scores were 0.4230 (`sales_dashboard_drd.md#2`) and 0.4183 (`products_sttm.md#0`).

## Result and what I learned

- Increasing `top_k` from 3 to 15 did not change the top-three order; it added more candidate context, with scores declining from 0.4884 to 0.4183.
- For a RAG prompt, `top_k=3` is the sensible starting point for this query: it returns the highest-ranked evidence while avoiding 12 extra chunks that may dilute context and consume tokens.
- Increase `top_k` only if evaluation shows the needed answer is often missing from the first few chunks. A larger top-k is not automatically better; inspect the extra chunks for relevance.
- The query refers to a specific data-quality issue, and the first two results are the DQ rules and order STTM. This is an observed ranking, not proof every returned chunk directly answers the question; check chunk text before treating retrieval as a hit.

## Notes

The notebook-authentication notice appeared on the query calls but was informational.

