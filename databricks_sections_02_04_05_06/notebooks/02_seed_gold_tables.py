# Databricks notebook source
# MAGIC %md
# MAGIC # Seed the gold tables (Genie, app and agent exercises)
# MAGIC Creates `dim_customer`, `dim_product` and `fact_orders` from `seed_data.py` with table and column comments.
# MAGIC Safe to re-run: tables are overwritten.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

# MAGIC %run ./seed_data

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, LongType, StringType, StructField, StructType

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")

region_by_customer = {c[0]: c[2] for c in CUSTOMERS}

customers_df = spark.createDataFrame(
    CUSTOMERS,
    StructType([
        StructField("customer_id", LongType()),
        StructField("customer_name", StringType()),
        StructField("region", StringType()),
        StructField("segment", StringType()),
    ]),
)
products_df = spark.createDataFrame(
    PRODUCTS,
    StructType([
        StructField("product_id", LongType()),
        StructField("product_name", StringType()),
        StructField("category", StringType()),
        StructField("unit_price", DoubleType()),
    ]),
)
orders_df = spark.createDataFrame(
    [(o[0], o[1], o[2], region_by_customer[o[1]], o[3], *o[4:]) for o in ORDERS],
    StructType([
        StructField("order_id", LongType()),
        StructField("customer_id", LongType()),
        StructField("product_id", LongType()),
        StructField("region", StringType()),
        StructField("quantity", IntegerType()),
        StructField("order_date", StringType()),
        StructField("promised_date", StringType()),
        StructField("ship_date", StringType()),
        StructField("delivered_date", StringType()),
        StructField("order_status", StringType()),
    ]),
)
for date_column in ["order_date", "promised_date", "ship_date", "delivered_date"]:
    orders_df = orders_df.withColumn(date_column, F.to_date(F.col(date_column)))

# COMMAND ----------

def _quote(text):
    return text.replace("'", "''")


for name, frame in [("dim_customer", customers_df), ("dim_product", products_df), ("fact_orders", orders_df)]:
    table = f"{CATALOG}.{SCHEMA}.{name}"
    frame.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(table)
    spark.sql(f"COMMENT ON TABLE {table} IS '{_quote(TABLE_COMMENTS[name])}'")
    for column, comment in COLUMN_COMMENTS[name].items():
        spark.sql(f"ALTER TABLE {table} ALTER COLUMN {column} COMMENT '{_quote(comment)}'")
    print(f"{table}: {spark.table(table).count()} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sanity check (should print 24 orders, 2 cancelled)

# COMMAND ----------

display(spark.sql(f"SELECT order_status, COUNT(*) AS orders FROM {ORDERS_TABLE} GROUP BY order_status ORDER BY order_status"))
