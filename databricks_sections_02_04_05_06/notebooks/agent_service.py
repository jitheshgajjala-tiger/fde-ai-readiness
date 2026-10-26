"""Serving-compatible adapter for the FDE order-fulfilment agent."""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any

import mlflow
from databricks.ai_search.client import AISearchClient
from databricks.sdk import WorkspaceClient
from databricks_openai import DatabricksOpenAI
from mlflow.models import ModelConfig
from mlflow.pyfunc import ResponsesAgent
from mlflow.types.responses import ResponsesAgentRequest, ResponsesAgentResponse

logger = logging.getLogger(__name__)
model_config = ModelConfig()

SYSTEM_PROMPT = (
    "You answer questions about customer orders and company policy. Use a tool whenever the answer depends on data or "
    "documents; answer directly only for general questions such as arithmetic. If a tool returns NOT_FOUND, say the order "
    "was not found. For a question requiring both order analytics and policy/document facts, call ask_genie and "
    "search_docs respectively, then combine their results. Never invent order data."
)
MAX_STEPS = 6


def _schema(name: str, description: str, parameter: str, kind: str) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {parameter: {"type": kind}},
                "required": [parameter],
            },
        },
    }


TOOL_SCHEMAS = [
    _schema("get_order_status", "Get the status of one order by id.", "order_id", "integer"),
    _schema("get_late_days", "Get how many days late one order was delivered, by order id.", "order_id", "integer"),
    _schema("ask_genie", "Ask a natural-language analytics question about orders, revenue, regions or delivery rates.", "question", "string"),
    _schema("search_docs", "Search policy and mapping documents (returns, shipping, STTM, data quality rules).", "query", "string"),
]


class OrderFulfilmentAgent(ResponsesAgent):
    """ResponsesAgent wrapper around the notebook's tool-calling workflow."""

    def load_context(self, context: Any) -> None:
        self.workspace = WorkspaceClient()
        self.llm = DatabricksOpenAI()
        self.ai_search = AISearchClient(disable_notice=True)
        self.warehouse_id = model_config.get("sql_warehouse_id")
        self.catalog = model_config.get("catalog")
        self.schema = model_config.get("schema")
        self.genie_space_id = model_config.get("genie_space_id")
        self.chat_model_endpoint = model_config.get("chat_model_endpoint")
        self.ai_search_endpoint = model_config.get("ai_search_endpoint")
        self.ai_search_index_name = model_config.get("ai_search_index_name")
        self._index = self.ai_search.get_index(
            endpoint_name=self.ai_search_endpoint,
            index_name=self.ai_search_index_name,
        )

    @mlflow.trace(span_type="TOOL")
    def get_order_status(self, order_id: int) -> str:
        statement = f"SELECT {self.catalog}.{self.schema}.get_order_status({int(order_id)})"
        return str(self._query_scalar(statement))

    @mlflow.trace(span_type="TOOL")
    def get_late_days(self, order_id: int) -> str:
        statement = f"SELECT {self.catalog}.{self.schema}.get_late_days({int(order_id)})"
        return str(self._query_scalar(statement))

    def _query_scalar(self, statement: str) -> Any:
        result = self.workspace.statement_execution.execute_statement(
            statement=statement,
            warehouse_id=self.warehouse_id,
            catalog=self.catalog,
            schema=self.schema,
            wait_timeout="50s",
        )
        while result.status.state.value in {"PENDING", "RUNNING"}:
            time.sleep(1)
            result = self.workspace.statement_execution.get_statement(result.statement_id)
        if result.status.state.value != "SUCCEEDED":
            raise RuntimeError(
                f"SQL Statement Execution failed ({result.status.state.value}): "
                f"{result.status.error}"
            )
        rows = result.result.data_array if result.result else None
        return rows[0][0] if rows else None

    @mlflow.trace(span_type="TOOL")
    def ask_genie(self, question: str) -> str:
        base = f"/api/2.0/genie/spaces/{self.genie_space_id}"
        started = self.workspace.api_client.do(
            "POST", f"{base}/start-conversation", body={"content": question}
        )
        conversation_id = started["conversation_id"]
        message_id = started["message_id"]
        deadline = time.time() + 300
        while time.time() < deadline:
            message = self.workspace.api_client.do(
                "GET", f"{base}/conversations/{conversation_id}/messages/{message_id}"
            )
            if message["status"] in {"COMPLETED", "FAILED", "CANCELLED"}:
                break
            time.sleep(3)
        else:
            raise TimeoutError("Genie did not answer within 300 seconds")
        if message["status"] != "COMPLETED":
            error = message.get("error") or {}
            return f"Genie failed ({error.get('type', 'UNKNOWN')}): {error.get('error', message['status'])}"
        attachments = message.get("attachments") or []
        text_parts = []
        for attachment in attachments:
            if attachment.get("text"):
                text_parts.append(attachment["text"].get("content", ""))
            if attachment.get("query"):
                result = self.workspace.api_client.do(
                    "GET",
                    f"{base}/conversations/{conversation_id}/messages/{message_id}/attachments/"
                    f"{attachment['attachment_id']}/query-result",
                )
                rows = result["statement_response"]["result"].get("data_array")
                text_parts.append(
                    f"SQL: {attachment['query'].get('query')}\nROWS: {rows}"
                )
        return "\n".join(text_parts) or f"Genie completed with status {message['status']}."

    @mlflow.trace(span_type="RETRIEVER")
    def search_docs(self, query: str) -> str:
        rows = self._index.similarity_search(
            query_text=query,
            columns=["chunk_id", "text"],
            num_results=3,
            query_type="hybrid",
        )["result"]["data_array"]
        return "\n".join(f"[{row[0]}] {row[1]}" for row in rows)

    def _execute_tool(self, name: str, arguments: dict[str, Any]) -> str:
        functions = {
            "get_order_status": self.get_order_status,
            "get_late_days": self.get_late_days,
            "ask_genie": self.ask_genie,
            "search_docs": self.search_docs,
        }
        if name not in functions:
            raise ValueError(f"unknown agent tool: {name}")
        return str(functions[name](**arguments))

    def predict(self, request: ResponsesAgentRequest) -> ResponsesAgentResponse:
        messages = self.prep_msgs_for_cc_llm(request.input)
        if not any(message.get("role") == "system" for message in messages):
            messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
        for _ in range(MAX_STEPS):
            reply = self.llm.chat.completions.create(
                model=self.chat_model_endpoint,
                messages=messages,
                tools=TOOL_SCHEMAS,
            ).choices[0].message
            if not reply.tool_calls:
                final_text = reply.content or ""
                return ResponsesAgentResponse(
                    output=[self.create_text_output_item(text=final_text, id=str(uuid.uuid4()))]
                )
            messages.append(reply)
            for call in reply.tool_calls:
                arguments = json.loads(call.function.arguments)
                try:
                    tool_output = self._execute_tool(call.function.name, arguments)
                except Exception as exc:
                    logger.exception("agent tool failed: %s", call.function.name)
                    tool_output = f"TOOL_ERROR: {type(exc).__name__}: {exc}"
                messages.append(
                    {"role": "tool", "tool_call_id": call.id, "content": tool_output}
                )
        final_text = "I could not finish within the allowed number of steps."
        return ResponsesAgentResponse(
            output=[self.create_text_output_item(text=final_text, id=str(uuid.uuid4()))]
        )


mlflow.models.set_model(OrderFulfilmentAgent())
