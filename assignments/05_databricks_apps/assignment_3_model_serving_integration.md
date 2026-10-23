# Assignment 3: Model-serving integration

**Section:** 5. Databricks Apps

Wire the app to call a deployed model-serving endpoint and display the response, handling a failure/timeout case gracefully in the UI.

## Deliverables

- [ ] Approach and steps taken
- [ ] Evidence (screenshots, output, or links)
- [ ] Result and what I learned

## Notes

The app has a **Model endpoint** tab and displays a friendly UI error while logging the underlying exception. This workspace has no traditional Model Serving endpoint listed; its available resource is the Unity Gateway **Model** service for Claude Sonnet 4.5 with **Can execute** permission. The app now invokes that resource through the OpenAI-compatible Unity Gateway route (`/ai-gateway/mlflow/v1/chat/completions`), using the fully qualified model-service name provided by the `model` resource in `SERVING_ENDPOINT`.

Test one valid prompt and capture the displayed model response. Then temporarily use an invalid model-service name, redeploy, and capture the friendly failure message. Restore the valid resource and redeploy afterward. This assignment remains pending until both live success and failure cases are observed.

