"""Unit tests for scripts/lab_utils.py — no RustFS required."""

import sys
import types

import pytest

sys.path.insert(0, "scripts")
import lab_utils


def test_get_s3_client_returns_client():
    client = lab_utils.get_s3_client()
    assert hasattr(client, "list_buckets")
    assert hasattr(client, "put_object")
    assert hasattr(client, "get_object")


def test_get_s3_client_custom_params():
    client = lab_utils.get_s3_client(
        endpoint="http://localhost:9999",
        access_key="mykey",
        secret_key="mysecret",
        region="eu-west-1",
    )
    assert client.meta.endpoint_url == "http://localhost:9999"


def test_wait_for_server_timeout():
    # Should fail quickly on a port that has nothing listening
    result = lab_utils.wait_for_server(endpoint="http://localhost:19999", timeout=2)
    assert result is False
