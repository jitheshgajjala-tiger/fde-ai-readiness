# Databricks notebook source
# MAGIC %md
# MAGIC # Tool-calling agent, tracing and evaluation (Section 6, Assignments 1 to 4)
# MAGIC A plain tool-calling loop over a Databricks model service, with MLflow tracing.
# MAGIC Run cells from the top in order. Run `07_uc_functions` first. Do not replace the Agent loop cell with a stub.
# MAGIC Assignment 1 uses UC functions; Assignment 2 enables Genie and document search.
# MAGIC
# MAGIC Deployment (Assignment 5) is **not** in this notebook: Databricks' recommended path changes between releases, so
# MAGIC follow the current quickstart linked in the runbook.

# COMMAND ----------

# MAGIC %pip install databricks-openai databricks-ai-search mlflow --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

# MAGIC %run ./eval_data

# COMMAND ----------

import json
import time

import mlflow
from databricks.ai_search.client import AISearchClient
from databricks.sdk import WorkspaceClient
from databricks_openai import DatabricksOpenAI

mlflow.openai.autolog()
w = WorkspaceClient()
llm = DatabricksOpenAI()

A1_TOOLS = ["get_order_status", "get_late_days"]
A2_TOOLS = [*A1_TOOLS, "ask_genie", "search_docs"]
ENABLED_TOOLS = A1_TOOLS.copy()
MAX_STEPS = 6

SYSTEM_PROMPT = (
    "You answer questions about customer orders and company policy. Use a tool whenever the answer depends on data or "
    "documents; answer directly only for general questions such as arithmetic. If a tool returns NOT_FOUND, say the order "
    "was not found. For a question that asks for both order analytics and policy/document facts, call ask_genie and "
    "search_docs respectively, then combine their results. Never invent order data."
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Tools

# COMMAND ----------

GENIE_BASE = f"/api/2.0/genie/spaces/{GENIE_SPACE_ID}"


@mlflow.trace(span_type="TOOL")
def get_order_status(order_id: int) -> str:
    return spark.sql(f"SELECT {CATALOG}.{SCHEMA}.get_order_status({int(order_id)})").first()[0]


@mlflow.trace(span_type="TOOL")
def get_late_days(order_id: int) -> str:
    return spark.sql(f"SELECT {CATALOG}.{SCHEMA}.get_late_days({int(order_id)})").first()[0]


@mlflow.trace(span_type="TOOL")
def ask_genie(question: str) -> str:
    if not GENIE_SPACE_ID:
        raise ValueError("ask_genie needs GENIE_SPACE_ID in 00_config")
    started = w.api_client.do("POST", f"{GENIE_BASE}/start-conversation", body={"content": question})
    cid, mid = started["conversation_id"], started["message_id"]
    deadline = time.time() + 300
    while time.time() < deadline:
        message = w.api_client.do("GET", f"{GENIE_BASE}/conversations/{cid}/messages/{mid}")
        if message["status"] in {"COMPLETED", "FAILED", "CANCELLED"}:
            break
        time.sleep(3)
    else:
        raise TimeoutError("genie did not answer within 300 seconds")
    if message["status"] != "COMPLETED":
        return f"Genie could not answer (status {message['status']})."
    parts = []
    for attachment in message.get("attachments") or []:
        if attachment.get("text"):
            parts.append(attachment["text"].get("content", ""))
        if attachment.get("query"):
            result = w.api_client.do(
                "GET", f"{GENIE_BASE}/conversations/{cid}/messages/{mid}/attachments/{attachment['attachment_id']}/query-result"
            )
            parts.append(f"SQL: {attachment['query'].get('query')}\nROWS: {result['statement_response']['result'].get('data_array')}")
    return "\n".join(parts) or "Genie returned no content."


_ai_search_index = None


@mlflow.trace(span_type="RETRIEVER")
def search_docs(query: str) -> str:
    global _ai_search_index
    if _ai_search_index is None:
        _ai_search_index = AISearchClient(disable_notice=True).get_index(
            endpoint_name=AI_SEARCH_ENDPOINT, index_name=INDEX_NAME
        )
    rows = _ai_search_index.similarity_search(
        query_text=query, columns=["chunk_id", "text"], num_results=3, query_type="hybrid"
    )["result"]["data_array"]
    return "\n".join(f"[{row[0]}] {row[1]}" for row in rows)


TOOL_FUNCTIONS = {f.__name__: f for f in [get_order_status, get_late_days, ask_genie, search_docs]}


def _schema(name, description, parameter, kind):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": {parameter: {"type": kind}}, "required": [parameter]},
        },
    }


TOOL_SCHEMAS = {
    "get_order_status": _schema("get_order_status", "Get the status of one order by id.", "order_id", "integer"),
    "get_late_days": _schema("get_late_days", "Get how many days late one order was delivered, by order id.", "order_id", "integer"),
    "ask_genie": _schema("ask_genie", "Ask a natural-language analytics question about orders, revenue, regions or delivery rates.", "question", "string"),
    "search_docs": _schema("search_docs", "Search policy and mapping documents (returns, shipping, STTM, data quality rules).", "query", "string"),
}

# COMMAND ----------

# MAGIC %md
# MAGIC ## Agent loop

# COMMAND ----------

@mlflow.trace(span_type="AGENT")
def run_agent(question: str) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": question}]
    tools = [TOOL_SCHEMAS[name] for name in ENABLED_TOOLS]
    for _ in range(MAX_STEPS):
        reply = llm.chat.completions.create(model=CHAT_MODEL_ENDPOINT, messages=messages, tools=tools).choices[0].message
        if not reply.tool_calls:
            return reply.content
        messages.append(reply)
        for call in reply.tool_calls:
            arguments = json.loads(call.function.arguments)
            try:
                output = str(TOOL_FUNCTIONS[call.function.name](**arguments))
            except Exception as exc:  # return the failure to the model so it can explain it; the trace keeps the exception
                output = f"TOOL_ERROR: {type(exc).__name__}: {exc}"
            messages.append({"role": "tool", "tool_call_id": call.id, "content": output})
    return "I could not finish within the allowed number of steps."

# COMMAND ----------

# MAGIC %md
# MAGIC ## Assignment 1: calls the tool when needed, answers directly when not
# MAGIC This cell selects the two UC tools. Run it to verify Assignment 1 behavior.

# COMMAND ----------

for question in ["What is the status of order 1007?", "What is 15% of 200?"]:
    print(question, "->", run_agent(question))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Assignment 2: combined Genie and document-search question
# MAGIC This cell enables all four tools, asks one question requiring both structured order data and policy context,
# MAGIC and creates an MLflow trace. Confirm the trace contains both `ask_genie` and `search_docs` tool spans.

# COMMAND ----------

ENABLED_TOOLS = A2_TOOLS.copy()
combined_question = (
    "How many orders were cancelled, and how many days do customers have to return unused products?"
)
combined_answer = run_agent(combined_question)
print(combined_answer)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Assignment 3: evaluation (14 questions, expected answers computed from the seed data)
# MAGIC This evaluation uses the tool set selected above. Record the observed failures and inspect their traces.

# COMMAND ----------

import re


def _normalise(text):
    return text.lower().replace(",", "").replace("$", "")


def _contains(answer, expected):
    # Whole-token match so that the expected answer "2" does not pass on "24".
    return re.search(r"(?<![\w.])" + re.escape(expected) + r"(?![\w])", answer) is not None


def _passes(row, answer):
    answer = _normalise(answer)
    expected = [_normalise(e) for e in row["expected_any"]]
    return all(_contains(answer, e) for e in expected) if row.get("match") == "all" else any(_contains(answer, e) for e in expected)


results = []
for row in EVAL_ROWS:
    answer = run_agent(row["question"])
    results.append({"needs": row["needs"], "question": row["question"], "passed": _passes(row, answer), "answer": answer[:120]})

import pandas as pd

report = pd.DataFrame(results)
display(report)
print(f"passed {report.passed.sum()} of {len(report)} with tools {ENABLED_TOOLS}")
print(report.groupby("needs").passed.agg(["sum", "count"]))
