# Assignment 2: Freshness test

**Section:** 4. Vector Database Creation in Databricks

Insert a new row into the source Delta table after the index is built, and verify (and time) how long it takes for that row to become retrievable through the index — document the sync behavior.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (notebook output recorded below)
- [x] Result and what I learned

## Approach

Inserted a uniquely named probe row into `workspace.fde_prep.doc_chunks`, triggered the Delta Sync index, then polled the index every 10 seconds for the row. The notebook's reported duration starts immediately after the insert and includes sync plus polling delay.

## Evidence

```text
sync triggered after 2.6 s
row became searchable after seconds: 44.7
```

## Result and what I learned

- The new row became retrievable about **44.7 seconds after insertion** on this run.
- Triggering sync returned in 2.6 seconds; that is not the same as the row being queryable. The full freshness latency was about 44.7 seconds.
- This is one measurement on a small sample table and is not a service-level guarantee. Repeated runs and a larger table would be needed for a reliable latency estimate.

## Notes

The probe row is temporary test data. The notebook excludes `source = 'probe.md'` from the direct-index comparison.

