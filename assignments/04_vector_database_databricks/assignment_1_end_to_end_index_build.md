# Assignment 1: End-to-end index build

**Section:** 4. Vector Database Creation in Databricks

Starting from a Delta table with CDF enabled, create a Vector Search endpoint and a Delta Sync Index, and run a basic `similarity_search` query against it.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (notebook output and top-hit results)
- [x] Result and what I learned

## Approach

1. Seeded `workspace.fde_prep.doc_chunks` as a Delta table with Change Data Feed enabled.
2. Created the standard AI Search endpoint `fde_prep_endpoint`.
3. Created the Delta Sync index `workspace.fde_prep.doc_chunks_index`, using `chunk_id` as the key and the `text` column with the `databricks-qwen3-embedding-0-6b` embedding endpoint.
4. Queried it for `How is order_total calculated?` and returned the top three chunks.

## Evidence

Provisioning output:

```text
index ready=True message=Index creation succeeded.
top hits:
sales_dashboard_drd.md#1  doc_type=drd   score=0.6064
orders_sttm.md#0          doc_type=sttm  score=0.5548
orders_sttm.md#1          doc_type=sttm  score=0.5106
```

Index in Catalog Explorer: `workspace.fde_prep.doc_chunks_index`.

## Result and what I learned

- The managed endpoint, Delta Sync index and similarity query all completed successfully.
- The top result was the sales dashboard DRD, not the orders STTM. Retrieval is relevant but not guaranteed to return the exact chunk first; the later filter and tuning experiments help assess this.
- This is a small 24-chunk demonstration corpus. It verifies the build path, not production retrieval quality.

## Notes

The endpoint is billable while it exists. Delete it after the remaining Section 4 exercises are captured.

