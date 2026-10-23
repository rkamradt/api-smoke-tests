"""
Smoke tests for Grafana.
In-cluster URL: http://grafana.monitoring:3000
Requires: GRAFANA_API_KEY env var (inject via Helm secretRef)
"""
import pytest


def test_health(http, grafana_base_url):
    # /api/health requires no auth
    r = http.get(f"{grafana_base_url}/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body.get("database") == "ok"


def test_datasources_reachable(http, grafana_base_url, grafana_api_key):
    if not grafana_api_key:
        pytest.skip("GRAFANA_API_KEY not set")
    r = http.get(
        f"{grafana_base_url}/api/datasources",
        headers={"Authorization": f"Bearer {grafana_api_key}"},
    )
    assert r.status_code == 200
    assert isinstance(r.json(), list)
