"""
Smoke tests for Axon Server.
In-cluster URL: http://axon-server.axon-server:8024
"""


def test_health(http, axon_base_url):
    r = http.get(f"{axon_base_url}/actuator/health")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "UP"


def test_info(http, axon_base_url):
    r = http.get(f"{axon_base_url}/actuator/info")
    assert r.status_code == 200
