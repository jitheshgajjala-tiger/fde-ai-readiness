# Assignment 3: Metadata-filtered retrieval

**Section:** 3. Retrieval-Augmented Generation (RAG)

Add a metadata field (e.g., document type or sector) to your chunks, and build a query that filters retrieval to only the relevant subset before answering.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (experiment output and results)
- [x] Result and what I learned

## Approach

Run with `python experiments.py a3` in `section_03_rag/`.

- Each chunk carries a `doc_type` field taken from its folder: `sttm`, `drd` or `policy`.
- `retrieve_dense(..., doc_type=...)` applies the filter **before** ranking, so chunks of other types can never appear in the results.
- Test question: "How are cancelled orders handled?" This is deliberately ambiguous, because "cancelled orders" appears in the shipping policy, the sales dashboard DRD and the orders STTM.

## Evidence

| Filter | Top-3 results (score) |
|---|---|
| none | `shipping_policy.md#1` (0.80, policy), `sales_dashboard_drd.md#1` (0.74, drd), `returns_policy.md#0` (0.70, policy) |
| `doc_type=sttm` | `orders_sttm.md#1` (0.66), `orders_sttm.md#0` (0.63), `products_sttm.md#1` (0.61) |
| `doc_type=policy` | `shipping_policy.md#1` (0.80), `returns_policy.md#0` (0.70), `returns_policy.md#1` (0.68) |

## Result and what I learned

- The filter works as intended: every result under `sttm` is an STTM chunk, and every result under `policy` is a policy chunk.
- Without a filter, the top-3 contained **no** STTM chunk at all, so a data engineer asking about the pipeline logic would get customer-policy text. The filter turns an ambiguous question into a scoped one.
- A filter guarantees scope, **not** relevance. Under `sttm` the third result (`products_sttm.md#1`) is unrelated; it only ranks there because the other STTM chunks are exhausted.
- In Databricks Vector Search, the same idea is the `filters` argument of `similarity_search`, applied to a metadata column synced from the Delta table (Assignment 3 of Section 4).

## Notes

