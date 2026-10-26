# Databricks notebook source
# MAGIC %md
# MAGIC # Shared configuration
# MAGIC Run with `%run ./00_config` at the top of every other notebook. Edit the values in the next cell once.

# COMMAND ----------

CATALOG = spark.sql("SELECT current_catalog()").first()[0]  # change if you should use a different catalog
SCHEMA = "fde_prep"

CUSTOMERS_TABLE = f"{CATALOG}.{SCHEMA}.dim_customer"
PRODUCTS_TABLE = f"{CATALOG}.{SCHEMA}.dim_product"
ORDERS_TABLE = f"{CATALOG}.{SCHEMA}.fact_orders"
CHUNKS_TABLE = f"{CATALOG}.{SCHEMA}.doc_chunks"

# Fill these in after the matching step in the runbook.
GENIE_SPACE_ID = "01f1ce6ccd6f1af2a95d58d046af219e"  # Order Fulfilment Analytics
SQL_WAREHOUSE_ID = "ce72158123970c93"  # Serverless Starter Warehouse

# Names to confirm with 01_preflight (the endpoint names differ between workspaces).
CHAT_MODEL_ENDPOINT = "databricks-claude-sonnet-4-5"
EMBEDDING_ENDPOINT = "databricks-qwen3-embedding-0-6b"

AI_SEARCH_ENDPOINT = "fde_prep_endpoint"
INDEX_NAME = f"{CATALOG}.{SCHEMA}.doc_chunks_index"

print(f"Using {CATALOG}.{SCHEMA}")
