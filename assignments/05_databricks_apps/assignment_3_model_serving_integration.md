# Assignment 3: Model-serving integration

**Section:** 5. Databricks Apps

Wire the app to call a deployed model-serving endpoint and display the response, handling a failure/timeout case gracefully in the UI.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (successful response and failure output)
- [x] Result and what I learned

## Notes

The app has a **Model endpoint** tab and displays a friendly UI error while logging the underlying exception. This workspace has no traditional Model Serving endpoint listed; its available resource is the Unity Gateway **Model** service for Claude Sonnet 4.5 with **Can execute** permission. The app invokes that resource through the OpenAI-compatible Unity Gateway route (`/ai-gateway/mlflow/v1/chat/completions`), using the fully qualified model-service name provided by the `model` resource in `SERVING_ENDPOINT`.

## Successful request

Prompt: "In one sentence, explain how an AI model could help summarize customer support tickets. Don't claim access to this app's order data."

Observed response: "An AI model can analyze customer support tickets to extract key information like issue type, urgency, and main complaint, then generate concise summaries that help support teams quickly understand and prioritize cases without reading full ticket details."

The deployed app returned a relevant answer and did not claim to access its order data.

## Failure test

Temporarily configured `SERVING_ENDPOINT` with the invalid model-service name `system.ai.assignment_test_missing_model`, redeployed, and clicked **Send** with the same prompt. The app displayed: `The request failed: NotFound. Check the app logs for details.` The app log identified Databricks `NotFound` for the specified model service. This confirms the UI handles a missing service gracefully and directs the user to logs.

The valid Unity Gateway Claude Sonnet 4.5 resource mapping has been restored in `app.yaml` as `valueFrom: model` and pushed to the repository. Redeploy this restored configuration to leave the live app operational after the failure test; that final redeployment has not yet been confirmed.

## Result and what I learned

- A valid request returned a relevant response without claiming access to order data.
- An invalid model-service name produced a visible, friendly failure message instead of an unhandled traceback in the app UI.
- This workspace uses a Unity Gateway model service rather than a traditional Model Serving endpoint, so the app calls the Unity Gateway OpenAI-compatible route.

