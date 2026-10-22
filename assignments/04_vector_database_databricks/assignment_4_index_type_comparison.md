# Assignment 4: Index type comparison

**Section:** 4. Vector Database Creation in Databricks

Build one Delta Sync Index and one Direct Vector Access Index over the same conceptual dataset, and document the tradeoffs you observed (setup effort, update behavior, control).

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (notebook output recorded below)
- [x] Result and what I learned

## Approach

Compared two indexes over the same 24 document chunks using the same `databricks-qwen3-embedding-0-6b` model and question, `How is order_total calculated?`:

- Delta Sync index: `workspace.fde_prep.doc_chunks_index`, embeddings computed by Databricks from the `text` source column.
- Direct Vector Access index: `workspace.fde_prep.doc_chunks_index_direct`, embeddings computed by the notebook and explicitly upserted into the index.

## Evidence

Direct index reported `embedding dimension: 1024` and `ONLINE_DIRECT_ACCESS`. Its top results were:

| Rank | Chunk | Score |
|---|---|---:|
| 1 | `sales_dashboard_drd.md#1` | 0.6597 |
| 2 | `orders_sttm.md#0` | 0.6420 |
| 3 | `orders_sttm.md#1` | 0.5546 |

The Delta Sync index returned the same three chunks in the same order, with scores 0.6064, 0.5548 and 0.5106 respectively.

## Result and what I learned

- Both index types were queryable over the same chunk corpus and returned the same top-three ordering for this query. The scores differ, so I compare the ranked chunks, not assume the numeric values are interchangeable across index types.
- Delta Sync was simpler to maintain for table-backed source data: the source table is authoritative and a triggered sync propagates changes.
- Direct Vector Access required an extra embedding request and an explicit upsert. That provides direct control over vector content and update timing, but the caller owns keeping the index fresh.
- This comparison demonstrates the workflow trade-off on one query and a small corpus; it is not a performance or quality benchmark.

## Notes

The first direct-index query ran while the index was still provisioning and returned `BadRequest: index is not ready`. Waiting for `ONLINE_DIRECT_ACCESS` and for upsert updates to finish resolved it. A later rerun initially attempted to create the same index again; the corrected notebook now checks for and reuses an existing index.

