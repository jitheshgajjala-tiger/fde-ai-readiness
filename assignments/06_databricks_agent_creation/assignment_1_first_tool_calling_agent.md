# Assignment 1: First tool-calling agent

**Section:** 6. Databricks Agent Creation (Mosaic AI Agent Framework)

Register one Unity Catalog Function (e.g., a simple lookup or calculation) as a tool, and build an agent that correctly decides when to call it vs. answer directly.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (Databricks run output and MLflow trace details)
- [x] Result and what I learned

## Notes

Ran `07_uc_functions.py` and `08_agent.py` with `ENABLED_TOOLS = ["get_order_status", "get_late_days"]`. The agent answered the status question for order 1007 as `DELIVERED`, and the MLflow trace shows the `get_order_status` tool span and its output. For the general question `What is 15% of 200?`, the agent answered `30` directly. This demonstrates tool use for order data and a direct answer when no data tool is needed.

The notebook output records the successful direct UC-function check. I did not record the additional late-days question for order 1011; it is an optional extra check beyond the assignment's core tool-versus-direct-answer requirement.

