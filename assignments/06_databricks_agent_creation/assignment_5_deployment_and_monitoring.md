# Assignment 5: Deployment and monitoring

**Section:** 6. Databricks Agent Creation (Mosaic AI Agent Framework)

Deploy the agent to a Model Serving endpoint, send it a few live requests, and show how you'd monitor its behavior (latency, error rate, or a sample of logged interactions) after deployment.

## Approach

Prepared a Model Serving path in `databricks_sections_02_04_05_06/notebooks/agent_service.py` and `databricks_sections_02_04_05_06/notebooks/09_deploy_agent.py`. The serving adapter retains all four Section 6 tools, uses Databricks Statement Execution rather than notebook-only `spark`, and declares the chat endpoint, SQL warehouse, UC functions, Genie space, and AI Search index as MLflow resources. Running the deployment notebook logs/registers the model in Unity Catalog and creates or updates a CPU, scale-to-zero endpoint; this has workspace and billing effects.

The live deployment registered model version 3 and the endpoint reached `READY` on served model `fde_order_fulfilment_agent-4`. An initial update collided with provisioning already in progress; the notebook now waits for an active update to finish before applying endpoint configuration.

## Evidence

Observed from the 2026-10-23 run:

- Initial typed-SDK requests reported `success` for order 1007 (10.534 seconds) and arithmetic (1.844 seconds), served by `fde_order_fulfilment_agent-4`; their SDK response object exposed only the served-model header.
- Follow-up direct invocation using the ResponsesAgent payload returned the answer `The status of order 1007 is **DELIVERED**.` in 5.497 seconds.
- Follow-up direct invocation for `What is 15% of 200?` returned `15% of 200 is 30.` in approximately 1.993 seconds.
- Endpoint state was `READY`, `NOT_UPDATING`.
- Serving logs showed Gunicorn and workers starting without a startup error in the displayed excerpt.
- Corrected smoke test: order 1007 returned `The status of order 1007 is **DELIVERED**.` in 5.867 seconds.
- Corrected smoke test: `What is 15% of 200?` returned `15% of 200 is 30.` in 1.932 seconds.
- Endpoint state was `READY`, `NOT_UPDATING`.
- Metrics snapshot for served model `fde_order_fulfilment_agent-4`: model-prediction histogram count 4 and sum 11,620.5 ms (about 2.905 seconds mean across that metric bucket); model-queue histogram count 4 and sum about 5.473 ms. Request and request-latency series showed zero in the displayed snapshot, despite the successful invocations, so treat those series as stale/inconsistent rather than evidence of zero requests.
- The displayed serving-log excerpt showed Gunicorn and workers starting, with no startup failure in that excerpt.
- No MLflow trace screenshot was captured. It is supplementary; the live endpoint responses, latency, endpoint state, metrics, and serving-log output above provide the deployment and monitoring evidence.

## Result and what I learned

Assignment 5 is complete based on the live deployment, two successful smoke requests, endpoint status, latency measurements, metrics, and serving logs. MLflow is used to register and serve the model; a separate MLflow trace screenshot was not captured and is not needed to verify these results. The request-count series did not reflect the successful invocations in the captured metrics snapshot, so that discrepancy is noted rather than interpreted as zero traffic.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (screenshots, output, or links)
- [x] Result and what I learned

## Notes

The endpoint is separate from the Claude chat-model endpoint. The deployment notebook uses workspace resources from `00_config.py` and creates or updates a billable endpoint when its deployment cell runs. Do not commit secrets or unredacted logs.

