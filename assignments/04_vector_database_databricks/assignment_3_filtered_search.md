# Assignment 3: Filtered search

**Section:** 4. Vector Database Creation in Databricks

Add a metadata column (e.g., market or document category) to the source table and run a `similarity_search` query that combines vector similarity with a metadata filter.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (notebook output recorded below)
- [x] Result and what I learned

## Approach

Queried `workspace.fde_prep.doc_chunks` for `How are cancelled orders handled?` using the same AI Search index and top-4 setting, first without a filter and then with the metadata filters `doc_type = sttm` and `doc_type = policy`.

## Evidence

| Filter | Top results (chunk, score) |
|---|---|
| None | `orders_sttm.md#2` 0.6296; `shipping_policy.md#1` 0.5613; `sales_dashboard_drd.md#1` 0.5350; `shipping_policy.md#2` 0.5306 |
| `doc_type = sttm` | `orders_sttm.md#2` 0.6287; `orders_sttm.md#1` 0.4900; `products_sttm.md#2` 0.4646; `orders_sttm.md#0` 0.4536 |
| `doc_type = policy` | `shipping_policy.md#1` 0.5613; `shipping_policy.md#2` 0.5306; `returns_policy.md#0` 0.4615; `returns_policy.md#1` 0.4352 |

## Result and what I learned

- The filter restricts returned chunks to the requested document type. The STTM-filtered results are all STTM chunks; the policy-filtered results are all policy chunks.
- Without a filter, results mix technical mapping, shipping rules and dashboard context for the ambiguous phrase "cancelled orders". Filtering lets the caller set the intended scope.
- Filtering does not guarantee every result is directly relevant: for example, the STTM-filtered list includes `products_sttm.md#2` at rank 3. Inspect the returned text as well as the category.

## Notes

The SDK printed a notebook-authentication notice during queries. It was informational and did not prevent the results from returning.

