"""Creates the prep tables, UC functions and AI Search index in the workspace behind a Databricks CLI profile.

Usage: python provision_workspace.py <profile> <step> [<step> ...]   steps: tables, chunks, functions, search, cleanup
"""

import logging
import sys
import time
from pathlib import Path

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "notebooks"))

from seed_chunks import CHUNKS  # noqa: E402
from seed_data import COLUMN_COMMENTS, CUSTOMERS, ORDERS, PRODUCTS, TABLE_COMMENTS  # noqa: E402

logger = logging.getLogger(__name__)

CATALOG = "workspace"
SCHEMA = "fde_prep"
SEARCH_ENDPOINT = "fde_prep_endpoint"
EMBEDDING_ENDPOINT = "databricks-qwen3-embedding-0-6b"
INDEX_NAME = f"{CATALOG}.{SCHEMA}.doc_chunks_index"
CHUNKS_TABLE = f"{CATALOG}.{SCHEMA}.doc_chunks"


def _lit(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    return str(value)


def _date(value) -> str:
    return "NULL" if value is None else f"DATE'{value}'"


def _run(w: WorkspaceClient, warehouse_id: str, statement: str):
    response = w.statement_execution.execute_statement(statement=statement, warehouse_id=warehouse_id, wait_timeout="50s")
    while response.status.state in (StatementState.PENDING, StatementState.RUNNING):
        time.sleep(3)
        response = w.statement_execution.get_statement(response.statement_id)
    if response.status.state != StatementState.SUCCEEDED:
        raise RuntimeError(f"sql failed ({response.status.state}): {response.status.error.message if response.status.error else ''}\n{statement[:200]}")
    return response


def _create_table(w, wh, name, columns, comment, extra=""):
    column_sql = ", ".join(f"{col} {typ} COMMENT {_lit(COLUMN_COMMENTS[name][col])}" for col, typ in columns)
    _run(w, wh, f"CREATE OR REPLACE TABLE {CATALOG}.{SCHEMA}.{name} ({column_sql}) COMMENT {_lit(comment)} {extra}")


def step_tables(w, wh):
    _run(w, wh, f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
    region = {c[0]: c[2] for c in CUSTOMERS}
    _create_table(w, wh, "dim_customer", [("customer_id", "BIGINT"), ("customer_name", "STRING"), ("region", "STRING"), ("segment", "STRING")], TABLE_COMMENTS["dim_customer"])
    _run(w, wh, f"INSERT INTO {CATALOG}.{SCHEMA}.dim_customer VALUES " + ", ".join(f"({', '.join(map(_lit, c))})" for c in CUSTOMERS))
    _create_table(w, wh, "dim_product", [("product_id", "BIGINT"), ("product_name", "STRING"), ("category", "STRING"), ("unit_price", "DOUBLE")], TABLE_COMMENTS["dim_product"])
    _run(w, wh, f"INSERT INTO {CATALOG}.{SCHEMA}.dim_product VALUES " + ", ".join(f"({', '.join(map(_lit, p))})" for p in PRODUCTS))
    _create_table(
        w, wh, "fact_orders",
        [("order_id", "BIGINT"), ("customer_id", "BIGINT"), ("product_id", "BIGINT"), ("region", "STRING"), ("quantity", "INT"),
         ("order_date", "DATE"), ("promised_date", "DATE"), ("ship_date", "DATE"), ("delivered_date", "DATE"), ("order_status", "STRING")],
        TABLE_COMMENTS["fact_orders"],
    )
    rows = [
        f"({o[0]}, {o[1]}, {o[2]}, {_lit(region[o[1]])}, {o[3]}, {_date(o[4])}, {_date(o[5])}, {_date(o[6])}, {_date(o[7])}, {_lit(o[8])})"
        for o in ORDERS
    ]
    _run(w, wh, f"INSERT INTO {CATALOG}.{SCHEMA}.fact_orders VALUES " + ", ".join(rows))
    logger.info("step_tables: %d customers, %d products, %d orders", len(CUSTOMERS), len(PRODUCTS), len(ORDERS))


def step_chunks(w, wh):
    _run(w, wh, f"CREATE OR REPLACE TABLE {CHUNKS_TABLE} (chunk_id STRING, source STRING, doc_type STRING, text STRING) "
                "COMMENT 'Document chunks used for retrieval exercises. chunk_id is the primary key.' "
                "TBLPROPERTIES (delta.enableChangeDataFeed = true)")
    values = ", ".join(f"({_lit(c['chunk_id'])}, {_lit(c['source'])}, {_lit(c['doc_type'])}, {_lit(c['text'])})" for c in CHUNKS)
    _run(w, wh, f"INSERT INTO {CHUNKS_TABLE} VALUES {values}")
    logger.info("step_chunks: %d chunks", len(CHUNKS))


def step_functions(w, wh):
    orders = f"{CATALOG}.{SCHEMA}.fact_orders"
    _run(w, wh, f"""CREATE OR REPLACE FUNCTION {CATALOG}.{SCHEMA}.get_order_status(order_id BIGINT COMMENT 'Order id, for example 1007')
RETURNS STRING
COMMENT 'Returns the status of one order (PROCESSING, SHIPPED, DELIVERED or CANCELLED), or NOT_FOUND when the order id does not exist.'
RETURN COALESCE((SELECT MAX(o.order_status) FROM {orders} o WHERE o.order_id = get_order_status.order_id), 'NOT_FOUND')""")
    _run(w, wh, f"""CREATE OR REPLACE FUNCTION {CATALOG}.{SCHEMA}.get_late_days(order_id BIGINT COMMENT 'Order id, for example 1011')
RETURNS STRING
COMMENT 'Returns how many days after the promised date an order was delivered (negative means early). Returns NOT_DELIVERED when the order has no delivery date and NOT_FOUND when the order id does not exist.'
RETURN COALESCE((SELECT MAX(CASE WHEN o.delivered_date IS NULL THEN 'NOT_DELIVERED' ELSE CAST(datediff(o.delivered_date, o.promised_date) AS STRING) END)
                 FROM {orders} o WHERE o.order_id = get_late_days.order_id), 'NOT_FOUND')""")
    check = _run(w, wh, f"SELECT {CATALOG}.{SCHEMA}.get_order_status(1007), {CATALOG}.{SCHEMA}.get_late_days(1011), "
                        f"{CATALOG}.{SCHEMA}.get_order_status(9999), {CATALOG}.{SCHEMA}.get_late_days(1008)")
    logger.info("step_functions: expected [DELIVERED, 3, NOT_FOUND, NOT_DELIVERED], got %s", check.result.data_array[0])


def step_search(w, wh):
    from databricks.sdk.service.vectorsearch import (
        DeltaSyncVectorIndexSpecRequest, EmbeddingSourceColumn, EndpointType, PipelineType, VectorIndexType,
    )

    names = [e.name for e in w.vector_search_endpoints.list_endpoints()]
    if SEARCH_ENDPOINT not in names:
        logger.info("step_search: creating endpoint %s", SEARCH_ENDPOINT)
        w.vector_search_endpoints.create_endpoint_and_wait(name=SEARCH_ENDPOINT, endpoint_type=EndpointType.STANDARD)
    existing = [i.name for i in w.vector_search_indexes.list_indexes(endpoint_name=SEARCH_ENDPOINT)]
    if INDEX_NAME not in existing:
        w.vector_search_indexes.create_index(
            name=INDEX_NAME,
            endpoint_name=SEARCH_ENDPOINT,
            primary_key="chunk_id",
            index_type=VectorIndexType.DELTA_SYNC,
            delta_sync_index_spec=DeltaSyncVectorIndexSpecRequest(
                source_table=CHUNKS_TABLE,
                pipeline_type=PipelineType.TRIGGERED,
                embedding_source_columns=[EmbeddingSourceColumn(name="text", embedding_model_endpoint_name=EMBEDDING_ENDPOINT)],
            ),
        )
    deadline = time.time() + 1800
    while time.time() < deadline:
        status = w.vector_search_indexes.get_index(INDEX_NAME).status
        logger.info("step_search: index ready=%s message=%s", status.ready, status.message)
        if status.ready:
            break
        time.sleep(30)
    else:
        raise TimeoutError("index was not ready after 30 minutes")
    result = w.vector_search_indexes.query_index(
        index_name=INDEX_NAME, columns=["chunk_id", "doc_type"], query_text="How is order_total calculated?", num_results=3
    )
    logger.info("step_search: top hits %s", result.result.data_array)


def step_cleanup(w, wh):
    w.vector_search_indexes.delete_index(INDEX_NAME)
    w.vector_search_endpoints.delete_endpoint(SEARCH_ENDPOINT)
    logger.info("step_cleanup: deleted %s and %s", INDEX_NAME, SEARCH_ENDPOINT)


STEPS = {"tables": step_tables, "chunks": step_chunks, "functions": step_functions, "search": step_search, "cleanup": step_cleanup}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if len(sys.argv) < 3:
        raise ValueError(f"usage: provision_workspace.py <profile> <step>...; steps: {sorted(STEPS)}")
    unknown = [s for s in sys.argv[2:] if s not in STEPS]
    if unknown:
        raise ValueError(f"unknown steps {unknown}; choose from {sorted(STEPS)}")
    w = WorkspaceClient(profile=sys.argv[1])
    warehouse_id = next(iter(w.warehouses.list())).id
    for name in sys.argv[2:]:
        logger.info("running step %s on warehouse %s", name, warehouse_id)
        STEPS[name](w, warehouse_id)


if __name__ == "__main__":
    main()
