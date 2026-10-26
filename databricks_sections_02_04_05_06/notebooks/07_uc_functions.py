# Databricks notebook source
# MAGIC %md
# MAGIC # Unity Catalog functions as agent tools (Section 6, Assignments 1 and 4)
# MAGIC Registers two governed SQL functions the agent can call. Run `02_seed_gold_tables` first.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

FN_STATUS = f"{CATALOG}.{SCHEMA}.get_order_status"
FN_LATE = f"{CATALOG}.{SCHEMA}.get_late_days"

spark.sql(f"""
CREATE OR REPLACE FUNCTION {FN_STATUS}(order_id BIGINT COMMENT 'Order id, for example 1007')
RETURNS STRING
COMMENT 'Returns the status of one order (PROCESSING, SHIPPED, DELIVERED or CANCELLED), or NOT_FOUND when the order id does not exist.'
RETURN COALESCE((SELECT MAX(o.order_status) FROM {ORDERS_TABLE} o WHERE o.order_id = get_order_status.order_id), 'NOT_FOUND')
""")

spark.sql(f"""
CREATE OR REPLACE FUNCTION {FN_LATE}(order_id BIGINT COMMENT 'Order id, for example 1011')
RETURNS STRING
COMMENT 'Returns how many days after the promised date an order was delivered (negative means early). Returns NOT_DELIVERED when the order has no delivery date and NOT_FOUND when the order id does not exist.'
RETURN COALESCE(
  (SELECT MAX(CASE WHEN o.delivered_date IS NULL THEN 'NOT_DELIVERED'
               ELSE CAST(datediff(o.delivered_date, o.promised_date) AS STRING) END)
   FROM {ORDERS_TABLE} o WHERE o.order_id = get_late_days.order_id),
  'NOT_FOUND')
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test the functions directly (expected: DELIVERED, 3, NOT_FOUND, NOT_DELIVERED)

# COMMAND ----------

display(spark.sql(f"""
SELECT {FN_STATUS}(1007) AS status_1007,
       {FN_LATE}(1011)   AS late_days_1011,
       {FN_STATUS}(9999) AS status_9999,
       {FN_LATE}(1008)   AS late_days_1008
"""))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Assignment 4: break one tool, then find it from the trace
# MAGIC Run the next cell *after* the agent works, ask the agent about order 1007 again, then open the MLflow trace
# MAGIC and find the tool span whose output is wrong. Do not read the agent code to find it. Restore afterwards.

# COMMAND ----------

BREAK_TOOL = False  # set True to break get_order_status on purpose

if BREAK_TOOL:
    spark.sql(f"""
    CREATE OR REPLACE FUNCTION {FN_STATUS}(order_id BIGINT)
    RETURNS STRING
    RETURN COALESCE((SELECT MAX(c.region) FROM {CUSTOMERS_TABLE} c WHERE c.customer_id = get_order_status.order_id), 'NOT_FOUND')
    """)
    print("get_order_status now reads the wrong table. Re-run the cell that created it to restore.")
