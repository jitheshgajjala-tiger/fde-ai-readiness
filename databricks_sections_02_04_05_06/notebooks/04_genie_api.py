# Databricks notebook source
# MAGIC %md
# MAGIC # Genie API (Assignment 4): start a conversation, follow up, extract SQL
# MAGIC Uses the documented REST endpoints (`/api/2.0/genie/spaces/...`) through the workspace client, so it does not
# MAGIC depend on a particular SDK version. Set `GENIE_SPACE_ID` in `00_config` first.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

import time

from databricks.sdk import WorkspaceClient

if not GENIE_SPACE_ID:
    raise ValueError("GENIE_SPACE_ID is empty; copy it from the Genie space URL into 00_config")

w = WorkspaceClient()
BASE = f"/api/2.0/genie/spaces/{GENIE_SPACE_ID}"
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED"}


def wait_for_message(conversation_id, message_id, timeout_s=600):
    """Poll with backoff until the message reaches a terminal status (docs: poll 1-5 s, stop after 10 min)."""
    deadline = time.time() + timeout_s
    delay = 2.0
    while time.time() < deadline:
        message = w.api_client.do("GET", f"{BASE}/conversations/{conversation_id}/messages/{message_id}")
        if message["status"] in TERMINAL:
            return message
        time.sleep(delay)
        delay = min(delay * 1.5, 30)
    raise TimeoutError(f"genie message {message_id} did not finish within {timeout_s} seconds")


def ask_new(question):
    started = w.api_client.do("POST", f"{BASE}/start-conversation", body={"content": question})
    return started["conversation_id"], wait_for_message(started["conversation_id"], started["message_id"])


def ask_follow_up(conversation_id, question):
    sent = w.api_client.do("POST", f"{BASE}/conversations/{conversation_id}/messages", body={"content": question})
    return wait_for_message(conversation_id, sent["message_id"])


def extract(message):
    """Return (generated SQL or None, text answer or None, query attachment id or None)."""
    sql_text, text, attachment_id = None, None, None
    for attachment in message.get("attachments") or []:
        if attachment.get("query"):
            sql_text = attachment["query"].get("query")
            attachment_id = attachment.get("attachment_id")
        if attachment.get("text"):
            text = attachment["text"].get("content")
    return sql_text, text, attachment_id


def fetch_rows(conversation_id, message):
    _, _, attachment_id = extract(message)
    if not attachment_id:
        return []
    result = w.api_client.do(
        "GET",
        f"{BASE}/conversations/{conversation_id}/messages/{message['message_id']}/attachments/{attachment_id}/query-result",
    )
    return result["statement_response"]["result"].get("data_array", [])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run: first question, then a follow-up in the same thread

# COMMAND ----------

conversation_id, first = ask_new("How many orders are there per region?")
print("status:", first["status"])
sql_text, text, _ = extract(first)
print("SQL:\n", sql_text)
print("rows:", fetch_rows(conversation_id, first))

# COMMAND ----------

follow_up = ask_follow_up(conversation_id, "Only count delivered orders.")
print("status:", follow_up["status"])
sql_text, text, _ = extract(follow_up)
print("SQL:\n", sql_text)
print("rows:", fetch_rows(conversation_id, follow_up))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Evidence checklist
# MAGIC * Both messages report `COMPLETED`.
# MAGIC * The second SQL adds a `DELIVERED` filter even though the question never repeated the table, which proves the thread context was used.
# MAGIC * Nothing in this notebook touched the Genie UI.
# MAGIC * Clean up test threads: `DELETE /api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}`.
