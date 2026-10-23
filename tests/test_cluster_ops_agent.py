"""
Smoke tests for Cluster Ops Agent (FastAPI/LangGraph).
In-cluster URL: http://cluster-ops-agent.cluster-ops-agent:8000
"""


def test_openapi_schema(http, cluster_ops_agent_base_url):
    r = http.get(f"{cluster_ops_agent_base_url}/openapi.json")
    assert r.status_code == 200
    body = r.json()
    assert "paths" in body


def test_health(http, cluster_ops_agent_base_url):
    # FastAPI convention — update path if the service uses a different one
    r = http.get(f"{cluster_ops_agent_base_url}/health")
    assert r.status_code == 200
