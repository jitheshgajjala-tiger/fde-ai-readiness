# Assignment 3: Model-serving integration

**Section:** 5. Databricks Apps

Wire the app to call a deployed model-serving endpoint and display the response, handling a failure/timeout case gracefully in the UI.

## Deliverables

- [ ] Approach and steps taken
- [ ] Evidence (screenshots, output, or links)
- [ ] Result and what I learned

## Notes

The app already has a **Model endpoint** tab, calls `serving_endpoints.query`, and displays a friendly UI error while logging the underlying exception. `app.yaml` maps `SERVING_ENDPOINT` to the App resource key `model`. In Databricks Apps, attach an available chat model-serving endpoint using that exact resource key before redeploying. The prep notebook config names `databricks-claude-sonnet-4-5` as the chat endpoint; first confirm that endpoint is deployed and selectable in this workspace.

Test one valid prompt and capture the displayed model response. Then temporarily use an invalid endpoint name (or a stopped endpoint), redeploy, and capture the friendly failure message. Restore the valid endpoint and redeploy afterward. This assignment remains pending until both live success and failure cases are observed.

