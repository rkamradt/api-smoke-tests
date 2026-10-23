"""
Smoke tests for MinIO object storage.
In-cluster URL: http://minio.minio:9000
Requires: MINIO_ACCESS_KEY, MINIO_SECRET_KEY env vars (inject via Helm secretRef)
"""
import pytest
from minio import Minio
from minio.error import S3Error


def test_liveness(http, minio_endpoint):
    # MinIO liveness probe — no auth required
    r = http.get(f"http://{minio_endpoint}/minio/health/live")
    assert r.status_code == 200


def test_readiness(http, minio_endpoint):
    r = http.get(f"http://{minio_endpoint}/minio/health/ready")
    assert r.status_code == 200


def test_list_buckets(minio_endpoint, minio_access_key, minio_secret_key):
    if not minio_access_key or not minio_secret_key:
        pytest.skip("MINIO_ACCESS_KEY / MINIO_SECRET_KEY not set")
    client = Minio(minio_endpoint, access_key=minio_access_key, secret_key=minio_secret_key, secure=False)
    buckets = client.list_buckets()
    assert isinstance(buckets, list)
