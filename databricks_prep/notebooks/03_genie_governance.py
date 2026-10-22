# Databricks notebook source
# MAGIC %md
# MAGIC # Genie governance check (Assignment 3)
# MAGIC Adds a row filter on `fact_orders.region` so a second user sees only one region. Genie queries run as the asking
# MAGIC user, so the filter must change Genie's answers without any change to the Genie space.
# MAGIC
# MAGIC **You need a second identity** (another user in the workspace). Fill in the three values below.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

OWNER_EMAIL = ""         # you: sees every region
SECOND_USER_EMAIL = ""   # the other identity: restricted
ALLOWED_REGION = "North"  # the only region the second user may see

if not OWNER_EMAIL or not SECOND_USER_EMAIL:
    raise ValueError("governance check needs OWNER_EMAIL and SECOND_USER_EMAIL to be set")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Grant the second user read access (the filter then restricts rows)

# COMMAND ----------

for statement in [
    f"GRANT USE CATALOG ON CATALOG {CATALOG} TO `{SECOND_USER_EMAIL}`",
    f"GRANT USE SCHEMA ON SCHEMA {CATALOG}.{SCHEMA} TO `{SECOND_USER_EMAIL}`",
    f"GRANT SELECT ON TABLE {CUSTOMERS_TABLE} TO `{SECOND_USER_EMAIL}`",
    f"GRANT SELECT ON TABLE {PRODUCTS_TABLE} TO `{SECOND_USER_EMAIL}`",
    f"GRANT SELECT ON TABLE {ORDERS_TABLE} TO `{SECOND_USER_EMAIL}`",
]:
    spark.sql(statement)
    print("ok:", statement)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Create and attach the row filter

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{SCHEMA}.region_filter(region STRING)
RETURNS BOOLEAN
RETURN IF(current_user() = '{OWNER_EMAIL}', TRUE, region = '{ALLOWED_REGION}')
""")
spark.sql(f"ALTER TABLE {ORDERS_TABLE} SET ROW FILTER {CATALOG}.{SCHEMA}.region_filter ON (region)")
print("Row filter attached. As the owner you still see all rows:")
display(spark.sql(f"SELECT region, COUNT(*) AS orders FROM {ORDERS_TABLE} GROUP BY region ORDER BY region"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Test as the second user
# MAGIC 1. Give the second user `CAN USE` on the SQL warehouse and `CAN RUN` on the Genie space.
# MAGIC 2. Sign in as the second user (private window) and ask Genie: *How many orders are there per region?*
# MAGIC 3. Expected: the owner sees North, South, East and West (24 orders). The second user sees only the allowed region.
# MAGIC 4. Capture both answers and the generated SQL (the SQL is identical; the rows differ).

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Undo (so later exercises see every row again)

# COMMAND ----------

# spark.sql(f"ALTER TABLE {ORDERS_TABLE} DROP ROW FILTER")
