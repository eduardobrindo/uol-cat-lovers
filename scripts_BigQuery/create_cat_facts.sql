CREATE TABLE `dante-causa.analytics.cat_facts` (
  fact_id STRING OPTIONS(description="Unique ID for the Fact"),
  version INT64 OPTIONS(description="Version number of the Fact"),
  text STRING OPTIONS(description="The Fact itself"),
  updated_at TIMESTAMP OPTIONS(description="Date in which Fact was last modified"),
  deleted BOOLEAN OPTIONS(description="Whether the Fact has been soft-deleted"),
  source STRING OPTIONS(description="Source from which the fact was found. Typically a URL"),
  sent_count INT64 OPTIONS(description="The number of times the Fact has been sent by the CatBot"),
  ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP() OPTIONS(description="Timestamp indicating when the data was inserted into the table (Partitioning key)")
)
-- PARTITIONING BY INGESTION DATE
PARTITION BY DATE(ingestion_timestamp)

-- CLUSTERING (Performance Optimization)
CLUSTER BY fact_id

OPTIONS(
  description="A single animal fact, updated daily via ETL process.",
  
  -- DATA RETENTION POLICY
  -- Partitions older than 1 year (365 days) will be automatically deleted by BigQuery
  partition_expiration_days=365
);