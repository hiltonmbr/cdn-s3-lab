# 🏠 RustFS Architecture

RustFS is a high-performance, **100% S3-compatible** distributed object storage system written in Rust. It leverages the language's memory safety and performance to deliver a lightweight, decentralized alternative to traditional storage systems.

## Decentralized, Peer-to-Peer Design

Unlike HDFS (which has a single NameNode acting as metadata master), RustFS adopts a **fully symmetric architecture** where all nodes are equal. There are no master nodes, no metadata servers, and no single points of failure.

![RustFS Architecture](https://docs.rustfs.com/assets/s2-1.C0TUhx6r.png)

Each RustFS node runs a single binary (~100 MB) that handles both data and metadata atomically. The cluster discovers nodes automatically and distributes data using deterministic hashing.

## Core Concepts

| Concept | Description |
|---|---|
| **Object** | The fundamental storage unit — any unstructured data (files, streams, blobs) |
| **Bucket** | Logical container for objects, analogous to a top-level directory |
| **Drive** | A physical disk or volume. RustFS requires exclusive access to each drive |
| **Set (Stripe)** | A group of drives from across the cluster. An object is stored within exactly one set |

A key architectural insight: **drives within a set are distributed across different nodes** to maximize fault tolerance. If you have 4 nodes with 1 drive each, a set of 4 drives spans all 4 nodes. If any 2 nodes fail, data remains recoverable (with EC:2).

## How Data Flows

1. A client sends a PUT request to any node (via load balancer)
2. RustFS splits the object into **k data shards** + **m parity shards** (Erasure Coding)
3. Shards are distributed across drives in the chosen set
4. Metadata (shard locations, checksums) is written atomically with data — **no separate metadata database**
5. On read, RustFS fetches any k shards and reconstructs the original object

## S3 Compatibility

RustFS implements the full S3 REST API, including:

- **Object operations:** PUT, GET, DELETE, HEAD, POST (multipart)
- **Bucket operations:** List, Create, Delete
- **Advanced features:** Versioning, Lifecycle policies, WORM (Object Lock), Bucket policies, Pre-signed URLs, CORS
- **Standard SDKs:** Works with `boto3`, `aws-cli`, `mc` (MinIO Client), and any S3-compatible tool

## Benefits Over HDFS

| Aspect | HDFS | RustFS |
|---|---|---|
| Architecture | Master-slave (NameNode bottleneck) | Peer-to-peer, fully symmetric |
| Redundancy | 3x replication (200% overhead) | Erasure Coding (25-100% overhead) |
| API | HDFS-specific (hdfs://) | Standard S3 REST API |
| Metadata | Separate database (fsimage + edits) | Inline, atomic with data |
| Deployment | Multiple roles, complex config | Single binary, one command |
| Single point of failure | NameNode (even with HA) | None — any node can serve |

In the next document, we'll see how Object Storage powers the modern Data Lakehouse architecture.
