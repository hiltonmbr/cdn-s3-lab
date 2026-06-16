# 🪣 Object Storage Lab: RustFS & Erasure Coding

### **The Practical Guide to Distributed Object Storage**
Explore the paradigm shift from HDFS to Object Storage, with hands-on labs covering Erasure Coding, fault tolerance, fragmentation, and the Medallion Lakehouse architecture — all running locally with Docker.

![Docker](https://img.shields.io/badge/Docker-27.x-2496ED?logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Compose-v2-2496ED?logo=docker&logoColor=white)
![RustFS](https://img.shields.io/badge/RustFS-1.0.0--beta.8-FF8C00?logo=rust&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 What is this repository?

A **hands-on lab** demonstrating the modern Object Storage paradigm. Where the Hadoop lab focused on HDFS (coupled compute+storage), this lab explores the decoupled architecture behind modern Data Lakes and Lakehouses.

- 📖 **Rich Documentation** — Theory-backed content on Object Storage, Erasure Coding (Reed-Solomon), fault tolerance, and fragmentation.
- ⚙️ **Single-Node RustFS Server** — A single S3-compatible storage server with **Erasure Coding** across 4 isolated drives, all running on your machine.
- 💻 **Interactive Labs** — Practice S3 API, Pandas integration, multipart uploads, fault injection, and more via Jupyter notebooks.

> **Target audience:** Data engineers, architects, and storage enthusiasts who want to understand how modern object storage systems handle durability, availability, and performance at scale.

---

## ⚡ Quick Start (5 minutes)

You need `docker`, `make`, and `uv` installed:

```bash
# 1. Clone the repository
git clone https://github.com/hiltonmbr/cdn-s3-lab.git
cd cdn-s3-lab

# 2. Start the single-node RustFS server (Erasure Coding enabled)
make up

# 3. Set up Python environment and launch the labs
make setup-env
make jupyter-lab
```

Your browser will open with the interactive notebooks in the `notebooks/` folder. Select `.venv` as the Python kernel.

Access the cluster:
- 👉 **[Admin Console](http://localhost:9001)** — credentials: `admin` / `adminpassword`
- 👉 **S3 API endpoint**: `http://localhost:9000`

---

## ⚙️ Prerequisites

| Requirement | Details |
|---|---|
| **Docker Engine** | Essential for instantiating the cluster in an isolated manner |
| **Docker Compose** | Already bundled in Docker Desktop |
| **Make (optional)** | Used for terminal shortcuts |
| **uv** | Fast Python package installer and resolver ([Installation](https://docs.astral.sh/uv/getting-started/installation/)) |
| **Resources** | At least **4GB RAM** recommended |
| **Disk** | A few GB free for labs 3–6 (datasets are downloaded to `temp/`) |

Verify the vital tools:

```bash
docker version
docker compose version
uv --version
```

---

## 🗺️ Learning Map

### 📖 Theory: Object Storage Fundamentals
Read the documentation in the `docs/` folder before the hands-on practice.

| # | Theoretical Module | What you will learn | Link |
|:---:|:---|:---|:---:|
| 1 | **The Object Storage Paradigm** | Why compute-storage separation changed everything | [📖 Read](docs/01-object-storage-paradigm.md) |
| 2 | **RustFS Architecture** | Peer-to-peer design, sets/stripes, S3 compatibility | [📖 Read](docs/02-rustfs-architecture.md) |
| 3 | **Data Lakehouse & Medallion** | Bronze/Silver/Gold, ACID on object storage | [📖 Read](docs/03-data-lakehouse.md) |
| 4 | **Erasure Coding & Reed-Solomon** | k/m/n parameters, storage efficiency, math behind EC | [📖 Read](docs/04-erasure-coding.md) |
| 5 | **Fault Tolerance & Self-Healing** | Node/disk failure, read-time repair, background scrub | [📖 Read](docs/05-fault-tolerance.md) |
| 6 | **Fragmentation & Multipart Upload** | Object sharding, parallel upload, resume on failure | [📖 Read](docs/06-multipart-fragmentation.md) |

### 🧪 Hands-on Labs: Getting Your Hands Dirty
Labs are inside the `notebooks/` folder. Open them via `make jupyter-lab` or VS Code with the Jupyter extension.

| # | Topic | Description | Link |
|:---:|:---|:---|:---:|
| 1 | 🪣 **Boto3 Basics** | Connect to S3 API, list/create buckets, upload/download objects | [🧪 Go to Lab](notebooks/01_boto3_basics.ipynb) |
| 2 | 🐼 **Pandas + Parquet (Medallion)** | Bronze→Silver→Gold pipeline using Pandas and Parquet | [🧪 Go to Lab](notebooks/02_pandas_s3fs_parquet.ipynb) |
| 3 | 🧩 **Multipart Upload & Fragmentation** | Upload large files in parallel, inspect parts, abort/resume | [🧪 Go to Lab](notebooks/03_multipart_upload.ipynb) |
| 4 | 🛡️ **Fault Tolerance Simulation** | Stop a node, verify data integrity via Erasure Coding | [🧪 Go to Lab](notebooks/04_fault_tolerance.ipynb) |
| 5 | 🔄 **Versioning & Lifecycle** | Object versioning, delete/restore, lifecycle rules | [🧪 Go to Lab](notebooks/05_versioning.ipynb) |
| 6 | 📊 **Erasure Coding In Practice** | Simulate multi-node failures, compare storage efficiency | [🧪 Go to Lab](notebooks/06_erasure_coding.ipynb) |

> 💡 **Labs 3–6** demonstrate advanced object storage features. Each notebook starts with small examples so you can validate the flow before scaling up.

---

## 🏗️ Lab Architecture

A single RustFS server manages 4 independent Docker volumes (`drive0`…`drive3`) that together form an Erasure Coding set — simulating a real multi-disk object storage node.

```
📁 cdn-s3-lab/
├── docker-compose.yml   → 1 server, 4 drives, Erasure Coding
├── notebooks/           → Interactive Jupyter labs
├── docs/                → Theoretical fundamentals
├── Makefile             → Convenience shortcuts
└── temp/                → Temporary downloads & datasets (git-ignored)
```

```mermaid
graph TD
    subgraph "Docker Compose — Single RustFS Server"
        sv["🖥️  rustfs-server<br>Port 9000 (S3 API)<br>Port 9001 (Admin Console)"]
        init["🪣 rustfs-init<br>Creates buckets: bronze/silver/gold"]

        d0["💾 drive0_data<br>📁 /data/drive0"]
        d1["💾 drive1_data<br>📁 /data/drive1"]
        d2["💾 drive2_data<br>📁 /data/drive2"]
        d3["💾 drive3_data<br>📁 /data/drive3"]

        sv --- d0 & d1 & d2 & d3
        init --> sv
    end

    subgraph "Erasure Coding (Reed-Solomon 4+2)"
        obj["📄 Object<br>10 MB"]
        d1_shard["🧩 Drive 0 — Data Shard 1<br>~1.25 MB"]
        d2_shard["🧩 Drive 1 — Data Shard 2<br>~1.25 MB"]
        d3_shard["🧩 Drive 2 — Data Shard 3<br>~1.25 MB"]
        d4_shard["🧩 Drive 3 — Data Shard 4<br>~1.25 MB"]
        p1["🛡️ Drive 0 — Parity 1<br>~1.25 MB"]
        p2["🛡️ Drive 1 — Parity 2<br>~1.25 MB"]

        obj --> d1_shard & d2_shard & d3_shard & d4_shard
        obj --> p1 & p2
    end

    subgraph "Fault Tolerance"
        f1["❌ drive0 lost<br>EC reconstructs from parity"]
        f2["❌ drive1 lost<br>Data remains accessible"]
        f3["✅ drive2 alive"]
        f4["✅ drive3 alive"]
        f5["💪 With EC 4+2, survives<br>up to 2 drive failures"]
    end

    subgraph "Local Environment (Compute)"
        jupyter["💻 Jupyter Lab<br>Pandas + Boto3"]
    end

    jupyter == "S3 API (boto3)" ==> sv

    classDef core fill:#f5f5f5,stroke:#569A31,stroke-width:2px;
    class sv,d0,d1,d2,d3,init core;
```

### Key Architectural Decisions

| Decision | Why |
|---|---|
| **4 drives** | Minimum for meaningful Erasure Coding (4+2 scheme) |
| **Docker volumes** | Each drive is a named volume — isolated and durable |
| **Single server** | No load balancer needed; RustFS handles the full S3 API natively |
| **Erasure Coding inline** | Every write is EC-encoded across all 4 drives; no separate process needed |

### 🆚 Single-Drive vs Erasure Coding (EC 4+2)

| Aspect | Single Drive (no EC) | Erasure Coding (4+2) |
|---|---|---|
| **Storage efficiency** | 100% (1 GB stored → 1 GB used) | 66% (1 GB stored → 1.5 GB used) |
| **Fault tolerance** | 0 drive failures | Up to 2 drive failures |
| **Durability** | Single point of failure | Survives simultaneous loss of any 2 drives |
| **Performance (write)** | Direct write | EC encoding adds ~15–30% CPU overhead |
| **Performance (read)** | Direct read | Read-time repair if drives are degraded |
| **Cost** | Lower storage cost | Higher storage cost, lower rebuild cost |
| **Use case** | Dev/test, ephemeral data | Production, regulatory compliance, critical data |

---

## 📝 Lab Administration Cheatsheet

```bash
# ── Server Orchestration ──
make up              # 🔥 Start the RustFS server (4 drives, Erasure Coding)
make down            # 😴 Stop the server
make clean           # 💥☢️ Nuke containers + volumes + local data
make clean-data      # 🧹 Wipe only temp/ downloads
make status          # 📡 Show running containers

# ── Accessing Terminal ──
make shell-server    # 🐚 rustfs-server shell

# ── Running Notebooks Locally ──
make setup-env       # 🐍 Create Python environment with uv
make jupyter-lab     # 📓🚀 Start Jupyter Lab
make strip           # 🧹 Strip notebook outputs (commit-safe)
```

---

## 📄 License and References

This project is made available under the [MIT License](LICENSE).

> **Open educational material.** Created for the hands-on classes of the **Data Science for Business** course (UFPB). Developed by Hilton Martins.

### References

- [RustFS Official Documentation](https://docs.rustfs.com)
- [Amazon S3 API Reference](https://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Apache Arrow / Parquet](https://parquet.apache.org)
- [The Data Lakehouse Architecture (Databricks)](https://www.databricks.com/blog/2020/01/30/what-is-a-data-lakehouse.html)
