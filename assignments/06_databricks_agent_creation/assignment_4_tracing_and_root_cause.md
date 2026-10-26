# Assignment 4: Tracing and root-cause

**Section:** 6. Databricks Agent Creation (Mosaic AI Agent Framework)

Deliberately break one tool (e.g., point it at the wrong table) and use MLflow tracing to identify exactly which step caused the wrong final answer, without re-reading the whole agent code from scratch.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (broken-result MLflow trace and restoration check)
- [x] Result and what I learned

## Notes

For the failure test, `BREAK_TOOL = True` replaced the order-status lookup with a customer-region lookup. The agent was asked, `What is the status of order 1007?` The answer was `The order 1007 was not found in the system.` The MLflow trace shows the `get_order_status` tool span receiving that question and returning the same incorrect result. This identifies the faulty tool output as the cause without needing to inspect the full agent implementation.

After capturing the failure trace, I restored the normal `get_order_status` function. A live SQL check then returned `DELIVERED` for order 1007, confirming the shared function was repaired. Do not leave `BREAK_TOOL` enabled or the function pointed at the wrong table.

## Result and what I learned

- The trace isolated `get_order_status` as the failing step: it returned `NOT_FOUND` for an existing order because the deliberately broken implementation queried customer IDs instead of order IDs.
- The agent's final answer followed the incorrect tool output, so the trace narrowed the root cause to the tool rather than the model's response generation.
- The UC function was restored and verified afterward: order 1007 returned `DELIVERED`.

