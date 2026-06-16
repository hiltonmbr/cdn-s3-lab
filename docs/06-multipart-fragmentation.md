# 🧩 Fragmentation & Multipart Upload

When you upload an object to S3-compatible storage, the system must decide how to handle it internally. This document explains how objects are fragmented (sharded) and how the **Multipart Upload API** enables efficient large-file transfers.

## Internal Fragmentation (Sharding)

In RustFS, every object is **automatically split into shards** during the write process:

1. The object is divided into **k data shards** (size depends on configuration)
2. **m parity shards** are computed via Erasure Coding
3. All **n = k + m** shards are distributed across drives in the set

This sharding happens transparently — clients only see the complete object.

### Shard Size

RustFS dynamically adjusts shard size (64 KB – 4 MB) based on object size:

| Object Size | Shard Size | Number of Data Shards |
|---|---|---|
| 1 MB | 64 KB | 16 |
| 100 MB | 1 MB | 100 |
| 1 GB | 4 MB | 256 |

## Multipart Upload (Client-Side Fragmentation)

For **large objects** (typically >100 MB), the S3 API provides the **Multipart Upload** feature. Instead of sending one massive PUT request, the client splits the file into **parts** and uploads each part independently.

### Why Multipart?

| Benefit | Description |
|---|---|
| **Parallel upload** | Upload multiple parts simultaneously, saturating available bandwidth |
| **Resume on failure** | Only failed parts need retransmission, not the entire file |
| **Maximum object size** | Single PUT is limited to 5 GB; multipart supports up to 5 TB |
| **Progress tracking** | Each part has an ETag for verification |
| **Pause/resume** | Upload session persists; resume hours or days later |

### How It Works

```
1. Initiate → Get UploadId
2. Upload Part 1 ──→ ETag: "abc123"
3. Upload Part 2 ──→ ETag: "def456"
4. Upload Part 3 ──→ ETag: "ghi789"
...
5. Complete → All parts merged into single object
```

### S3 API Calls

| Operation | Description |
|---|---|
| `CreateMultipartUpload` | Start the session, get UploadId |
| `UploadPart` | Upload a single part (with part number 1-10000) |
| `ListParts` | View uploaded parts and their ETags |
| `CompleteMultipartUpload` | Assemble all parts into the final object |
| `AbortMultipartUpload` | Cancel and discard all uploaded parts |

### Upload Strategy Comparison

| Method | Max Size | Failure Behavior | Speed |
|---|---|---|---|
| Single PUT | 5 GB | Full retransmit | Sequential |
| Multipart (serial) | 5 TB | Retransmit failed parts | Sequential |
| Multipart (parallel) | 5 TB | Retransmit failed parts | **Parallel — fastest** |

## Practical Guidelines

| Object Size | Recommended Approach |
|---|---|
| < 100 MB | Single PUT |
| 100 MB – 5 GB | Multipart with 5-50 MB parts |
| > 5 GB | **Required** — multipart only |
| > 100 GB | Multipart with 50-100 MB parts, parallelism ≥ 10 |

## In the Lab

In lab 3, you will:
1. Upload a single large file with multipart (in parallel)
2. List uploaded parts mid-session
3. Simulate a failure and resume
4. Compare single PUT vs multipart performance
5. See how RustFS internally shards the uploaded object across its 4 nodes
