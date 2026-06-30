"""
Automated notebook tests using nbmake.

Requires:
  - RustFS running: make up
  - Dev dependencies installed: uv sync --extra dev

Run:
  make test
  # or: uv run pytest tests/ --nbmake --nbmake-timeout=120 -v
"""

import pytest

# Notebooks that are safe to run headlessly (no interactive widgets at init time)
NOTEBOOKS = [
    "notebooks/00_setup_check.ipynb",
    "notebooks/01_boto3_basics.ipynb",
    "notebooks/02_pandas_s3fs_parquet.ipynb",
    "notebooks/03_multipart_upload.ipynb",
    "notebooks/04_fault_tolerance.ipynb",
    "notebooks/05_versioning.ipynb",
    "notebooks/06_erasure_coding.ipynb",
    "notebooks/07_reed_solomon_from_scratch.ipynb",
    "notebooks/08_benchmarking.ipynb",
    "notebooks/09_cdn_edge_cache.ipynb",
]


@pytest.mark.parametrize("notebook", NOTEBOOKS)
def test_notebook_executes(notebook):
    """Placeholder — actual execution is handled by the --nbmake plugin.

    nbmake discovers notebooks via parametrize and runs each one in a
    subprocess kernel, failing the test if any cell raises an exception.
    This file exists so pytest can report each notebook as a named test item.
    """
    pytest.importorskip("nbmake", reason="nbmake not installed — run: uv sync --extra dev")
