# 🪣 The Object Storage Paradigm

Until the mid-2010s, the gold standard for distributed storage in Big Data was **HDFS** (Hadoop Distributed File System). While revolutionary at the time, HDFS carried a critical structural limitation: **Storage and Compute were coupled on the same machine**.

## The Coupling Problem

In the Hadoop ecosystem, each DataNode simultaneously acts as:
- **Disk:** Stores HDFS data blocks.
- **CPU:** Executes processing tasks (MapReduce/Spark/YARN).

If you needed more storage capacity, you were forced to buy complete servers (with CPUs, RAM, etc.), generating excessive costs for unused compute power. Moreover, to guarantee data availability, **all nodes had to stay on 24/7**, consuming energy even when no processing was happening.

## The Solution: Object Storage (S3)

Amazon S3 (Simple Storage Service) introduced a radical approach: **object storage** fully decoupled from compute.

- **Decoupling:** Storage is an independent entity. You don't provision servers — you just save "objects" in "buckets" and access them via HTTP API.
- **Capacity & Cost:** Virtually infinite scaling, paying only for what you use. Cold data becomes extremely cheap.
- **Ephemeral Clusters:** With data safely in S3, you spin up a 100-node Spark cluster, process for 2 hours, write results back to S3, and **destroy the cluster**. You pay only for 2 hours of CPU!

> 💡 **The Paradigm Shift:** In classic Hadoop, you moved code to data (Data Locality). With Object Storage and modern high-speed networks, you read data over the network and process it in **on-demand compute clusters**.

## Key Concepts

| Concept | Description |
|---|---|
| **Object** | The fundamental unit — a file + metadata + unique ID |
| **Bucket** | A flat container for objects (like a top-level directory) |
| **Key** | The object's unique identifier within a bucket |
| **S3 API** | HTTP-based REST API (GET, PUT, DELETE, LIST) |
| **Erasure Coding** | Data redundancy via parity shards (replace replication) |

## What Changed

| Before (HDFS) | After (S3) |
|---|---|
| Compute must live near data | Compute is fully independent |
| 3x replication overhead (200%) | Erasure Coding overhead (25-100%) |
| Block-level storage | Object-level storage |
| Specific client libraries (hdfs://) | Universal HTTP API |
| NameNode is single point of failure | Fully symmetric, no master |

In the next document, we'll explore how RustFS implements this paradigm as a modern, high-performance S3-compatible object store.
