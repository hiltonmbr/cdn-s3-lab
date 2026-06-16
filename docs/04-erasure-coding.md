# 🔢 Erasure Coding & Reed-Solomon

Erasure Coding (EC) is the technology that enables Object Storage systems like RustFS to achieve high durability with far less overhead than traditional replication.

## The Problem with Replication

HDFS uses **3x replication** — each block is copied to 3 different DataNodes. This provides good durability but terrible storage efficiency:

| Scheme | Raw Data | Stored Data | Overhead | Efficiency |
|---|---|---|---|---|
| 3x Replication | 10 GB | 30 GB | +200% | 33% |
| 2x Replication | 10 GB | 20 GB | +100% | 50% |

For petabyte-scale storage, paying 200% overhead is enormously expensive.

## How Erasure Coding Works

Erasure Coding uses **Reed-Solomon (RS) codes**, a mathematical algorithm from algebraic coding theory. The core idea:

1. **Split** the original data into **k** equal-sized data shards
2. **Compute** **m** parity shards using matrix multiplication over a Galois Field
3. **Store** all **n = k + m** shards across different drives/nodes
4. **Recover** any lost shards using any **k** surviving shards

### EC Notation

EC schemes are written as **EC:M** or **RS(K,M)**:

| Scheme | Data (k) | Parity (m) | Total (n) | Survives | Efficiency |
|---|---|---|---|---|---|
| EC:2 (RS:4,2) | 4 | 2 | 6 | 2 failures | 4/6 = 67% |
| EC:4 (RS:4,4) | 4 | 4 | 8 | 4 failures | 4/8 = 50% |
| RS(10,4) | 10 | 4 | 14 | 4 failures | 10/14 = 71% |

### Visual Example: RS(4,2)

```
Original:  [A1][A2][A3][A4]   (4 data shards)
Parity:    [P1][P2]           (2 parity shards)
Total:     [A1][A2][A3][A4][P1][P2]  (6 shards across 6 drives)

If drives 1 and 3 fail:
           [X][A2][X][A4][P1][P2]
Recovery:  Solve 4 equations with 4 unknowns → [A1][A3] reconstructed!
```

## RustFS Erasure Coding In Practice

RustFS uses Reed-Solomon codes with SIMD-accelerated matrix operations (AVX2). The encoding is done **inline** during every write — there's no separate encoding process.

Key parameters:
- **Minimum cluster:** 4 nodes with 1 drive each (for EC:2)
- **Default parity:** Automatically calculated based on cluster size
- **Shard size:** Dynamically adjusted (64 KB – 4 MB)
- **Checksum:** Blake3 hashing per shard

## Storage Efficiency Comparison

For a 100 TB dataset:

| Scheme | Raw Stored | Usable | Cost Factor |
|---|---|---|---|
| 3x Replication | 300 TB | 100 TB | 3.0x |
| RS(4,2) — EC:2 | 150 TB | 100 TB | 1.5x |
| RS(6,2) | 133 TB | 100 TB | 1.33x |
| RS(10,4) | 140 TB | 100 TB | 1.4x |

EC delivers **50-70% reduction** in storage costs compared to 3x replication, with equal or better durability.

## Limitations

- **Compute cost:** Encoding/decoding requires CPU (negligible with SIMD)
- **Reconstruction latency:** Reading a failed shard requires fetching k shards and decoding (vs just reading one replica)
- **Small objects:** EC is less efficient for very small objects (RustFS handles this with dynamic shard sizing)

In the labs, you'll see EC in action: shutting down nodes, verifying data integrity, and measuring the storage efficiency.
