import os
import pytest
import httpx


TIMEOUT = float(os.getenv("SMOKE_TIMEOUT", "15"))


@pytest.fixture
def http():
    with httpx.Client(timeout=TIMEOUT) as client:
        yield client


@pytest.fixture
def fhir_base_url():
    return os.getenv("FHIR_BASE_URL", "http://priorauth-fhir.priorauth-fhir:8080/fhir")


@pytest.fixture
def ollama_base_url():
    return os.getenv("OLLAMA_BASE_URL", "http://ollama.llm:11434")


@pytest.fixture
def cluster_ops_agent_base_url():
    return os.getenv("CLUSTER_OPS_AGENT_BASE_URL", "http://cluster-ops-agent.cluster-ops-agent:8000")


@pytest.fixture
def axon_base_url():
    return os.getenv("AXON_BASE_URL", "http://axon-server.axon-server:8024")


@pytest.fixture
def grafana_base_url():
    return os.getenv("GRAFANA_BASE_URL", "http://grafana.monitoring:3000")


@pytest.fixture
def grafana_api_key():
    return os.getenv("GRAFANA_API_KEY", "")


@pytest.fixture
def minio_endpoint():
    return os.getenv("MINIO_ENDPOINT", "minio.minio:9000")


@pytest.fixture
def minio_access_key():
    return os.getenv("MINIO_ACCESS_KEY", "")


@pytest.fixture
def minio_secret_key():
    return os.getenv("MINIO_SECRET_KEY", "")
