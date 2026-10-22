# Databricks notebook source
# MAGIC %md
# MAGIC # Seed the document chunks table (AI Search / vector search exercises)
# MAGIC Loads the chunks produced from the Topic 3 documents (see `make_chunk_seed.py`) into a Delta table with
# MAGIC **Change Data Feed enabled**, which a Delta Sync index on a standard endpoint requires.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

# MAGIC %run ./seed_chunks

# COMMAND ----------

from pyspark.sql.types import StringType, StructField, StructType

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
schema = StructType([StructField(n, StringType()) for n in ["chunk_id", "source", "doc_type", "text"]])
chunks_df = spark.createDataFrame([(c["chunk_id"], c["source"], c["doc_type"], c["text"]) for c in CHUNKS], schema)
chunks_df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(CHUNKS_TABLE)
spark.sql(f"ALTER TABLE {CHUNKS_TABLE} SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")
spark.sql(f"COMMENT ON TABLE {CHUNKS_TABLE} IS 'Document chunks used for retrieval exercises. chunk_id is the primary key.'")
print(f"{CHUNKS_TABLE}: {spark.table(CHUNKS_TABLE).count()} chunks")
display(spark.sql(f"SELECT doc_type, COUNT(*) AS chunks FROM {CHUNKS_TABLE} GROUP BY doc_type ORDER BY doc_type"))
