# 🏗️ From Data Lake to Data Lakehouse

When data started migrating en masse from HDFS to S3, we lost some of the metadata management and transactional control that existed in the Hadoop ecosystem. Pure S3-based Data Lakes often turned into **"Data Swamps"** — loose files with no transaction control or rigid structure.

The industry's answer to this problem was the **Data Lakehouse** architecture and the standardization of data maturity layers (**Medallion Architecture**).

## Medallion Architecture (Bronze, Silver, Gold)

To keep S3 organized, we separate data logically (through buckets or prefixes) into 3 maturity levels:

- 🥉 **Bronze (Raw):** Raw data ingested directly from sources (APIs, logs, database dumps). No transformations applied. Useful for future auditing or reprocessing if failures occur downstream.
- 🥈 **Silver (Cleaned):** Processing (Spark, Pandas) reads from Bronze, cleans null records, converts date types, deduplicates, and saves in the optimized **Parquet** format.
- 🥇 **Gold (Business Ready):** Final aggregations, business rules applied, ready for consumption by BI dashboards (PowerBI, Tableau) or executive reports.

> 💡 **Lab note:** Our docker-compose starts RustFS with three pre-created buckets: `bronze`, `silver`, and `gold`.

## How It Works In Practice

```
Bronze (raw CSV/JSON) ──> [Clean/Validate] ──> Silver (Parquet) ──> [Aggregate] ──> Gold (Analytics-ready)
```

Each layer is a separate S3 bucket or prefix. Data flows through transformation processes (batch or streaming) that read from one layer and write to the next.

## Lakehouse Technologies

Formats like **Delta Lake**, **Apache Iceberg**, and **Apache Hudi** were created to run "on top" of S3 and add ACID properties (Atomicity, Consistency, Isolation, Durability). This converts the mere S3 repository into a modern "Lakehouse."

Key capabilities they add:
- **ACID transactions** — concurrent readers/writers don't corrupt data
- **Schema enforcement** — prevents bad data from being written
- **Time travel** — query data as of any point in time
- **Upserts/merges** — efficiently update existing records

In our lab, we'll use the Medallion pattern directly with Pandas and Parquet on RustFS — a simplified but fully functional Lakehouse workflow.
