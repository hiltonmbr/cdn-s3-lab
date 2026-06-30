"""Shared utilities for all cdn-s3-lab notebooks."""

from __future__ import annotations

import subprocess
import time

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

# Default RustFS connection settings
_ENDPOINT = "http://localhost:9000"
_ACCESS_KEY = "admin"
_SECRET_KEY = "adminpassword"
_REGION = "us-east-1"


def get_s3_client(
    endpoint: str = _ENDPOINT,
    access_key: str = _ACCESS_KEY,
    secret_key: str = _SECRET_KEY,
    region: str = _REGION,
) -> boto3.client:
    """Return a boto3 S3 client pre-configured for RustFS (or any path-style S3 endpoint)."""
    return boto3.client(
        service_name="s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
        use_ssl=False,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        ),
    )


def ensure_bucket(s3, bucket_name: str) -> None:
    """Create bucket if it does not already exist."""
    existing = {b["Name"] for b in s3.list_buckets()["Buckets"]}
    if bucket_name not in existing:
        s3.create_bucket(Bucket=bucket_name)
        print(f"✅ Created bucket: {bucket_name}")
    else:
        print(f"✅ Bucket already exists: {bucket_name}")


def cleanup_bucket(s3, bucket_name: str) -> None:
    """Delete all objects (including versions) in a bucket, then delete the bucket."""
    try:
        # Handle versioned objects
        paginator = s3.get_paginator("list_object_versions")
        for page in paginator.paginate(Bucket=bucket_name):
            for obj_type in ("Versions", "DeleteMarkers"):
                for obj in page.get(obj_type, []):
                    s3.delete_object(
                        Bucket=bucket_name,
                        Key=obj["Key"],
                        VersionId=obj["VersionId"],
                    )
        # Fall back to non-versioned objects
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get("Contents", []):
                s3.delete_object(Bucket=bucket_name, Key=obj["Key"])
        s3.delete_bucket(Bucket=bucket_name)
        print(f"🗑️  Deleted bucket: {bucket_name}")
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            print(f"ℹ️  Bucket {bucket_name!r} does not exist, nothing to clean.")
        else:
            raise


def fail_drive(container: str, bucket: str, drive: int) -> None:
    """Simulate a drive failure by renaming the bucket shard directory to *_FAILED.

    Uses directory rename (not chmod) because ENOENT is reliably raised on the
    next path lookup even with cached open file descriptors.
    """
    src = f"/data/drive{drive}/{bucket}"
    dst = f"{src}_FAILED"
    subprocess.run(
        ["docker", "exec", container, "sh", "-c", f"test -d {src} && mv {src} {dst} || true"],
        check=True,
        capture_output=True,
    )
    print(f"💥 Drive {drive} failed — {src} renamed to {dst}")


def restore_drive(container: str, bucket: str, drive: int) -> None:
    """Restore a previously failed drive by renaming *_FAILED back to its original path."""
    dst = f"/data/drive{drive}/{bucket}"
    src = f"{dst}_FAILED"
    subprocess.run(
        ["docker", "exec", container, "sh", "-c", f"test -d {src} && mv {src} {dst} || true"],
        check=True,
        capture_output=True,
    )
    print(f"✅ Drive {drive} restored — {src} renamed back to {dst}")


def restore_all_drives(container: str, bucket: str, num_drives: int = 4) -> None:
    """Restore all failed drives for a given bucket."""
    for drive in range(num_drives):
        restore_drive(container, bucket, drive)


def count_shards_per_drive(container: str, bucket: str, num_drives: int = 4) -> dict[int, int]:
    """Return the number of shard files per drive for the given bucket."""
    counts: dict[int, int] = {}
    for drive in range(num_drives):
        result = subprocess.run(
            ["docker", "exec", container, "find", f"/data/drive{drive}/{bucket}", "-type", "f"],
            capture_output=True,
            text=True,
        )
        counts[drive] = len([line for line in result.stdout.splitlines() if line.strip()])
    return counts


def wait_for_server(endpoint: str = _ENDPOINT, timeout: int = 30) -> bool:
    """Poll the RustFS health endpoint until it responds 200 or timeout expires."""
    import urllib.request
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"{endpoint}/minio/health/live", timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False
