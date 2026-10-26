# Databricks notebook source
# MAGIC %md
# MAGIC # Preflight: what does this workspace allow?
# MAGIC Run this first. Anything that prints `UNAVAILABLE` tells you which assignment needs a different plan.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
print("User:", w.current_user.me().user_name)
print("Catalog in use:", CATALOG)


def _report(label, call):
    try:
        print(f"{label}: {call()}")
    except Exception as exc:  # report the reason, never hide it
        print(f"{label}: UNAVAILABLE ({type(exc).__name__}: {exc})")


_report("Catalogs", lambda: [c.name for c in w.catalogs.list()])
_report("SQL warehouses (id, name)", lambda: [(wh.id, wh.name) for wh in w.warehouses.list()])
_report(
    "Foundation model endpoints",
    lambda: sorted(e.name for e in w.serving_endpoints.list() if e.name.startswith("databricks-")),
)
_report("All serving endpoints", lambda: sorted(e.name for e in w.serving_endpoints.list()))
_report("Apps", lambda: [a.name for a in w.apps.list()])

# COMMAND ----------

# MAGIC %md
# MAGIC ## AI Search (vector search) availability
# MAGIC Needs the `databricks-ai-search` package; skip this cell if the install is not allowed.

# COMMAND ----------

# MAGIC %pip install databricks-ai-search --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

from databricks.ai_search.client import AISearchClient

try:
    print("AI Search endpoints:", AISearchClient(disable_notice=True).list_endpoints())
except Exception as exc:
    print(f"AI Search: UNAVAILABLE ({type(exc).__name__}: {exc})")

# COMMAND ----------

# MAGIC %md
# MAGIC ## What to do with the output
# MAGIC 1. Put a warehouse id into `SQL_WAREHOUSE_ID` in `00_config`.
# MAGIC 2. If your chat or embedding model endpoint has a different name, change `CHAT_MODEL_ENDPOINT` / `EMBEDDING_ENDPOINT`.
# MAGIC 3. Anything `UNAVAILABLE` means that assignment needs the fallback listed in the runbook.
