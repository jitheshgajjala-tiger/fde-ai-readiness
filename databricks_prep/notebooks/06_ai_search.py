# Databricks notebook source
# MAGIC %md
# MAGIC # AI Search (vector search) exercises: Assignments 1 to 5 of Section 4
# MAGIC Run `05_seed_doc_chunks` first. Run the cells in order and record the printed evidence.
# MAGIC The Python package is `databricks-ai-search` (formerly `databricks-vectorsearch`).

# COMMAND ----------

# MAGIC %pip install databricks-ai-search --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

import time

from databricks.ai_search.client import AISearchClient
from databricks.sdk import WorkspaceClient

client = AISearchClient(disable_notice=True)
w = WorkspaceClient()


def wait_endpoint_online(name, timeout_s=1800):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        state = client.get_endpoint(name).get("endpoint_status", {}).get("state")
        print("endpoint state:", state)
        if state == "ONLINE":
            return
        time.sleep(30)
    raise TimeoutError(f"endpoint {name} was not ONLINE after {timeout_s} seconds")


def wait_index_ready(index, timeout_s=1800):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        status = index.describe().get("status", {})
        if status.get("ready"):
            return
        print("index state:", status.get("detailed_state") or status.get("message"))
        time.sleep(20)
    raise TimeoutError(f"index was not ready after {timeout_s} seconds")


def show(results, label):
    rows = results["result"]["data_array"]
    print(f"--- {label} ({len(rows)} rows; last column is the score)")
    for row in rows:
        print([str(v)[:60] for v in row])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Assignment 1: endpoint + Delta Sync index + first query

# COMMAND ----------

try:
    client.get_endpoint(AI_SEARCH_ENDPOINT)
    print("endpoint exists")
except Exception as exc:
    print(f"endpoint lookup failed ({type(exc).__name__}); creating it")
    client.create_endpoint(name=AI_SEARCH_ENDPOINT, endpoint_type="STANDARD")
wait_endpoint_online(AI_SEARCH_ENDPOINT)

# COMMAND ----------

if client.index_exists(endpoint_name=AI_SEARCH_ENDPOINT, index_name=INDEX_NAME):
    index = client.get_index(endpoint_name=AI_SEARCH_ENDPOINT, index_name=INDEX_NAME)
    print("reusing existing index", INDEX_NAME)
else:
    index = client.create_delta_sync_index(
        endpoint_name=AI_SEARCH_ENDPOINT,
        source_table_name=CHUNKS_TABLE,
        index_name=INDEX_NAME,
        pipeline_type="TRIGGERED",
        primary_key="chunk_id",
        embedding_source_column="text",
        embedding_model_endpoint_name=EMBEDDING_ENDPOINT,
    )
wait_index_ready(index)

# COMMAND ----------

results = index.similarity_search(
    query_text="How is order_total calculated?",
    columns=["chunk_id", "doc_type", "text"],
    num_results=3,
)
show(results, "A1 similarity search")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Assignment 2: freshness test
# MAGIC Inserts a row, triggers a sync, then times how long until the new row is searchable.

# COMMAND ----------

marker = f"zz{int(time.time())}"
new_text = f"Freshness probe {marker}: the warehouse closes on public holidays."
spark.sql(f"INSERT INTO {CHUNKS_TABLE} VALUES ('probe#{marker}', 'probe.md', 'policy', '{new_text}')")
inserted_at = time.time()
index.sync()
print("sync triggered after", round(time.time() - inserted_at, 1), "s")

found_after = None
while time.time() - inserted_at < 1200:
    hits = index.similarity_search(
        query_text=new_text, columns=["chunk_id"], num_results=3, query_type="hybrid"
    )["result"]["data_array"]
    if any(row[0] == f"probe#{marker}" for row in hits):
        found_after = time.time() - inserted_at
        break
    time.sleep(10)
print("row became searchable after seconds:", None if found_after is None else round(found_after, 1))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Assignment 3: filtered search
# MAGIC Same query with and without a metadata filter on `doc_type`.

# COMMAND ----------

query = "How are cancelled orders handled?"
show(index.similarity_search(query_text=query, columns=["chunk_id", "doc_type"], num_results=4), "no filter")
show(
    index.similarity_search(query_text=query, columns=["chunk_id", "doc_type"], num_results=4, filters={"doc_type": "sttm"}),
    "filter doc_type = sttm",
)
show(
    index.similarity_search(query_text=query, columns=["chunk_id", "doc_type"], num_results=4, filters={"doc_type": "policy"}),
    "filter doc_type = policy",
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Assignment 4: Direct Vector Access index (embeddings computed outside the index)

# COMMAND ----------

rows = spark.table(CHUNKS_TABLE).filter("source != 'probe.md'").collect()
embedded = w.serving_endpoints.query(name=EMBEDDING_ENDPOINT, input=[r["text"] for r in rows])
vectors = [item.embedding for item in embedded.data]
dimension = len(vectors[0])
print("embedding dimension:", dimension)

direct_name = f"{INDEX_NAME}_direct"
if client.index_exists(endpoint_name=AI_SEARCH_ENDPOINT, index_name=direct_name):
    direct = client.get_index(endpoint_name=AI_SEARCH_ENDPOINT, index_name=direct_name)
    print("reusing existing direct index", direct_name)
else:
    direct = client.create_direct_access_index(
        endpoint_name=AI_SEARCH_ENDPOINT,
        index_name=direct_name,
        primary_key="chunk_id",
        embedding_dimension=dimension,
        embedding_vector_column="text_vector",
        schema={"chunk_id": "string", "source": "string", "doc_type": "string", "text": "string", "text_vector": "array<float>"},
    )
wait_index_ready(direct)
direct.upsert([
    {"chunk_id": r["chunk_id"], "source": r["source"], "doc_type": r["doc_type"], "text": r["text"], "text_vector": v}
    for r, v in zip(rows, vectors)
])
direct.wait_until_ready(verbose=True, wait_for_updates=True)

query_vector = w.serving_endpoints.query(name=EMBEDDING_ENDPOINT, input=["How is order_total calculated?"]).data[0].embedding
show(direct.similarity_search(query_vector=query_vector, columns=["chunk_id", "doc_type"], num_results=3), "A4 direct access")

# COMMAND ----------

# MAGIC %md
# MAGIC Compare in the write-up: setup effort (the direct index needed manual embedding and upsert code),
# MAGIC update behaviour (delta sync followed the table after `sync()`; direct needs explicit upserts), and control.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Assignment 5: top_k 3 versus 15

# COMMAND ----------

query = "What happens to rows with a null key?"
for k in (3, 15):
    show(index.similarity_search(query_text=query, columns=["chunk_id", "doc_type"], num_results=k), f"top_k={k}")

# COMMAND ----------

# MAGIC %md
# MAGIC Look for the rank where relevant chunks stop and filler starts. Pick `top_k` just past that rank for a RAG prompt,
# MAGIC because every extra chunk costs prompt tokens and can distract the model.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Clean up (endpoints cost money while they exist)

# COMMAND ----------

# client.delete_index(endpoint_name=AI_SEARCH_ENDPOINT, index_name=direct_name)
# client.delete_index(endpoint_name=AI_SEARCH_ENDPOINT, index_name=INDEX_NAME)
# client.delete_endpoint(AI_SEARCH_ENDPOINT)
