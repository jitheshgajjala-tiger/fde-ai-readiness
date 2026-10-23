"""Streamlit app for the Databricks Apps assignments. Tabs appear as their resources are configured."""

import logging
import os
import time

import pandas as pd
import streamlit as st
from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT_SECONDS = 30


def _require_env(name: str) -> str:
    value = os.getenv(name, "")
    if not value or "REPLACE" in value:
        raise ValueError(f"app config {name} is not set; edit app.yaml")
    return value


def _user_token() -> str | None:
    """Return the forwarded user token when user authorization is on, else None (app identity)."""
    if os.getenv("USE_USER_AUTH", "false").lower() != "true":
        return None
    token = st.context.headers.get("x-forwarded-access-token")
    if not token:
        raise ValueError("USE_USER_AUTH is true but no x-forwarded-access-token header arrived; add the sql scope to the app")
    return token


def _workspace_client(token: str | None) -> WorkspaceClient:
    if token:
        cfg = Config(host=Config().host, token=token, auth_type="pat", http_timeout_seconds=REQUEST_TIMEOUT_SECONDS)
    else:
        cfg = Config(http_timeout_seconds=REQUEST_TIMEOUT_SECONDS)
    return WorkspaceClient(config=cfg)


def run_query(statement: str, token: str | None) -> pd.DataFrame:
    cfg = Config()
    http_path = f"/sql/1.0/warehouses/{_require_env('DATABRICKS_WAREHOUSE_ID')}"
    if token:
        connection = sql.connect(server_hostname=cfg.host, http_path=http_path, access_token=token)
    else:
        connection = sql.connect(server_hostname=cfg.host, http_path=http_path, credentials_provider=lambda: cfg.authenticate)
    with connection as conn, conn.cursor() as cursor:
        cursor.execute(statement)
        return cursor.fetchall_arrow().to_pandas()


def ask_genie(question: str, token: str | None) -> str:
    w = _workspace_client(token)
    base = f"/api/2.0/genie/spaces/{_require_env('GENIE_SPACE_ID')}"
    started = w.api_client.do("POST", f"{base}/start-conversation", body={"content": question})
    cid, mid = started["conversation_id"], started["message_id"]
    deadline = time.time() + 180
    while time.time() < deadline:
        message = w.api_client.do("GET", f"{base}/conversations/{cid}/messages/{mid}")
        if message["status"] in {"COMPLETED", "FAILED", "CANCELLED"}:
            break
        time.sleep(3)
    else:
        raise TimeoutError("Genie did not answer within 3 minutes")
    if message["status"] == "FAILED":
        error = message.get("error") or {}
        error_type = error.get("type", "UNKNOWN") if isinstance(error, dict) else "UNKNOWN"
        error_message = error.get("error", "No error details returned") if isinstance(error, dict) else str(error)
        logger.error("Genie request failed (%s): %s", error_type, error_message)
        return f"Genie failed ({error_type}): {error_message}"
    texts = [a["text"]["content"] for a in message.get("attachments") or [] if a.get("text")]
    queries = [a["query"]["query"] for a in message.get("attachments") or [] if a.get("query")]
    sql_blocks = [f"SQL:\n```sql\n{query}\n```" for query in queries]
    return "\n\n".join(texts + sql_blocks) or f"Genie finished with status {message['status']}."


def ask_model(prompt: str, token: str | None) -> str:
    response = _workspace_client(token).serving_endpoints.query(
        name=_require_env("SERVING_ENDPOINT"),
        messages=[ChatMessage(role=ChatMessageRole.USER, content=prompt)],
        max_tokens=300,
    )
    return response.choices[0].message.content


def friendly_error(exc: Exception) -> str:
    """Short message for the UI; the full exception goes to the app log."""
    logger.exception("request failed")
    if isinstance(exc, (TimeoutError, ConnectionError)) or "timed out" in str(exc).lower():
        return "The service did not respond in time. Try again in a moment."
    return f"The request failed: {type(exc).__name__}. Check the app logs for details."


st.set_page_config(page_title="FDE prep app", layout="wide")
st.title("Order fulfilment")

try:
    token = _user_token()
except ValueError as exc:
    st.error(str(exc))
    st.stop()

st.caption("Running as the signed-in user" if token else "Running as the app service principal")

orders_tab, genie_tab, model_tab = st.tabs(["Orders (SQL)", "Ask Genie", "Model endpoint"])

with orders_tab:
    if "orders_data" not in st.session_state:
        st.session_state.orders_data = None

    if st.button("Load orders"):
        try:
            st.session_state.orders_data = run_query(
                f"SELECT * FROM {_require_env('ORDERS_TABLE')} ORDER BY order_id LIMIT 100", token
            )
        except Exception as exc:
            st.error(friendly_error(exc))

    orders = st.session_state.orders_data
    if orders is not None:
        selected_region = "All regions"
        if "region" in orders.columns:
            regions = ["All regions", *sorted(orders["region"].dropna().astype(str).unique())]
            selected_region = st.selectbox("Region", regions)
            if selected_region != "All regions":
                orders = orders[orders["region"].astype(str) == selected_region]
        st.dataframe(orders, use_container_width=True)
        if "order_date" in orders.columns and not orders.empty:
            monthly_orders = orders.assign(
                month=pd.to_datetime(orders["order_date"]).dt.to_period("M").astype(str)
            )
            monthly_counts = monthly_orders.groupby("month").size().rename("orders")
            st.subheader("Orders by month")
            st.bar_chart(monthly_counts)
        export_region = selected_region.lower().replace(" ", "_")
        st.download_button(
            "Download filtered orders (CSV)",
            data=orders.to_csv(index=False),
            file_name=f"orders_{export_region}.csv",
            mime="text/csv",
        )

with genie_tab:
    if not os.getenv("GENIE_SPACE_ID"):
        st.info("Not configured yet: add the Genie space resource and GENIE_SPACE_ID in app.yaml (Assignment 2).")
    else:
        question = st.text_input("Ask a question about orders")
        if question and st.button("Ask Genie"):
            with st.spinner("Waiting for Genie"):
                try:
                    st.markdown(ask_genie(question, token))
                except Exception as exc:
                    st.error(friendly_error(exc))

with model_tab:
    if not os.getenv("SERVING_ENDPOINT"):
        st.info("Not configured yet: add the serving endpoint resource and SERVING_ENDPOINT in app.yaml (Assignment 3).")
    else:
        prompt = st.text_area("Prompt")
        if prompt and st.button("Send"):
            with st.spinner("Calling the model"):
                try:
                    st.write(ask_model(prompt, token))
                except Exception as exc:
                    st.error(friendly_error(exc))
