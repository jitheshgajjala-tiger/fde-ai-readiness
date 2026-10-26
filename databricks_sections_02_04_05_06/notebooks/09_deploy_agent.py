# Databricks notebook source
# MAGIC %md
# MAGIC # Section 6, Assignment 5: deploy and monitor the order agent
# MAGIC Run after `07_uc_functions`, Genie setup, and `06_ai_search` are ready.
# MAGIC This notebook installs its own model-code dependencies before logging the model.

# COMMAND ----------

# MAGIC %pip install databricks-openai databricks-ai-search mlflow --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

import time
from datetime import timedelta
from pathlib import Path

import mlflow
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors.platform import ResourceConflict
from databricks.sdk.service.serving import (
    EndpointCoreConfigInput,
    EndpointTag,
    ServedEntityInput,
    ServingModelWorkloadType,
)
from mlflow.models.resources import (
    DatabricksFunction,
    DatabricksGenieSpace,
    DatabricksServingEndpoint,
    DatabricksSQLWarehouse,
    DatabricksVectorSearchIndex,
)

w = WorkspaceClient()

# This logs/registers a model and creates or updates a billable endpoint.
RUN_DEPLOYMENT = True
MODEL_NAME = f"{CATALOG}.{SCHEMA}.fde_order_fulfilment_agent"
ENDPOINT_NAME = "fde-order-fulfilment-agent"

# COMMAND ----------

# Declare resources used by the serving process so Databricks can configure managed authentication.
agent_resources = [
    DatabricksServingEndpoint(endpoint_name=CHAT_MODEL_ENDPOINT),
    DatabricksSQLWarehouse(warehouse_id=SQL_WAREHOUSE_ID),
    DatabricksFunction(function_name=f"{CATALOG}.{SCHEMA}.get_order_status"),
    DatabricksFunction(function_name=f"{CATALOG}.{SCHEMA}.get_late_days"),
    DatabricksGenieSpace(genie_space_id=GENIE_SPACE_ID),
    DatabricksVectorSearchIndex(index_name=INDEX_NAME),
]

print("Deployment resources:")
for resource in agent_resources:
    print(resource)

# COMMAND ----------

if RUN_DEPLOYMENT:
    existing_endpoint_names = {
        endpoint.name for endpoint in w.serving_endpoints.list()
    }
    if ENDPOINT_NAME in existing_endpoint_names:
        endpoint = w.serving_endpoints.wait_get_serving_endpoint_not_updating(
            name=ENDPOINT_NAME,
            timeout=timedelta(minutes=30),
        )
        print("Endpoint is ready for configuration:", endpoint.name, endpoint.state)

    service_file = Path("agent_service.py").resolve()
    if not service_file.is_file():
        raise FileNotFoundError(f"agent_service.py is missing from the notebook folder: {service_file}")

    mlflow.set_registry_uri("databricks-uc")
    model_info = mlflow.pyfunc.log_model(
        name="fde_order_fulfilment_agent",
        python_model=str(service_file),
        registered_model_name=MODEL_NAME,
        resources=agent_resources,
        model_config={
            "catalog": CATALOG,
            "schema": SCHEMA,
            "sql_warehouse_id": SQL_WAREHOUSE_ID,
            "genie_space_id": GENIE_SPACE_ID,
            "chat_model_endpoint": CHAT_MODEL_ENDPOINT,
            "ai_search_endpoint": AI_SEARCH_ENDPOINT,
            "ai_search_index_name": INDEX_NAME,
        },
        pip_requirements=[
            "databricks-ai-search",
            "databricks-openai",
            "databricks-sdk",
        ],
    )
    model_version = str(model_info.registered_model_version)
    print(f"Registered model: {MODEL_NAME}, version {model_version}")

    environment_vars = {
        "CATALOG": CATALOG,
        "SCHEMA": SCHEMA,
        "SQL_WAREHOUSE_ID": SQL_WAREHOUSE_ID,
        "GENIE_SPACE_ID": GENIE_SPACE_ID,
        "CHAT_MODEL_ENDPOINT": CHAT_MODEL_ENDPOINT,
        "AI_SEARCH_ENDPOINT": AI_SEARCH_ENDPOINT,
        "AI_SEARCH_INDEX_NAME": INDEX_NAME,
    }
    served_entity = ServedEntityInput(
        entity_name=MODEL_NAME,
        entity_version=model_version,
        workload_type=ServingModelWorkloadType.CPU,
        workload_size="Small",
        scale_to_zero_enabled=True,
        environment_vars=environment_vars,
    )

    if ENDPOINT_NAME in existing_endpoint_names:
        for attempt in range(2):
            try:
                endpoint = w.serving_endpoints.update_config_and_wait(
                    name=ENDPOINT_NAME,
                    served_entities=[served_entity],
                )
                break
            except ResourceConflict:
                if attempt:
                    raise
                w.serving_endpoints.wait_get_serving_endpoint_not_updating(
                    name=ENDPOINT_NAME,
                    timeout=timedelta(minutes=30),
                )
        print(f"Updated endpoint: {endpoint.name}")
    else:
        endpoint = w.serving_endpoints.create_and_wait(
            name=ENDPOINT_NAME,
            config=EndpointCoreConfigInput(
                name=ENDPOINT_NAME,
                served_entities=[served_entity],
            ),
            description="MLflow ResponsesAgent for FDE order fulfilment exercises",
            tags=[EndpointTag(key="project", value="fde-readiness")],
        )
        print(f"Created endpoint: {endpoint.name}")

# COMMAND ----------

if RUN_DEPLOYMENT:
    # Exercise both the data-backed path and the direct-response path; retain response and latency as evidence.
    smoke_questions = [
        "What is the status of order 1007?",
        "What is 15% of 200?",
    ]
    for question in smoke_questions:
        started_at = time.perf_counter()
        try:
            response = w.api_client.do(
                "POST",
                f"/serving-endpoints/{ENDPOINT_NAME}/invocations",
                body={
                    "input": [{"role": "user", "content": question}],
                    "context": {},
                },
            )
            print({
                "question": question,
                "status": "success",
                "latency_seconds": round(time.perf_counter() - started_at, 3),
                "response": response,
            })
        except Exception as exc:
            print({
                "question": question,
                "status": "error",
                "latency_seconds": round(time.perf_counter() - started_at, 3),
                "error": f"{type(exc).__name__}: {exc}",
            })

    details = w.serving_endpoints.get(name=ENDPOINT_NAME)
    print("Endpoint status:", details.state)

    metrics = w.serving_endpoints.export_metrics(name=ENDPOINT_NAME)
    print("Endpoint metrics:")
    print(metrics.contents.read().decode("utf-8"))

    served_entities = details.config.served_entities or []
    if served_entities:
        served_model_name = served_entities[0].name
        logs = w.serving_endpoints.logs(
            name=ENDPOINT_NAME,
            served_model_name=served_model_name,
        )
        print(f"Latest serving logs for {served_model_name}:")
        print(logs.as_dict())
    else:
        print("No served model is available yet; inspect endpoint state and retry monitoring after it is ready.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Monitoring and cleanup
# MAGIC This cell prints request responses, latency, endpoint metrics, and recent serving logs. Also inspect MLflow traces
# MAGIC generated by agent/tool spans in the workspace UI and record the actual results in Assignment 5.
# MAGIC The endpoint is configured to scale to zero; delete it when the exercise is complete if it is no longer needed.
# MAGIC To remove it explicitly, run `w.serving_endpoints.delete(name=ENDPOINT_NAME)` in a separate cell.
