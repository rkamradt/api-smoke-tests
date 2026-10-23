"""
Smoke tests for HAPI FHIR R4 server.
In-cluster URL: http://priorauth-fhir.priorauth-fhir:8080/fhir
"""


def test_capability_statement(http, fhir_base_url):
    r = http.get(f"{fhir_base_url}/metadata")
    assert r.status_code == 200
    body = r.json()
    assert body["resourceType"] == "CapabilityStatement"
    assert body["fhirVersion"].startswith("4.")


def test_patient_search_returns_bundle(http, fhir_base_url):
    r = http.get(f"{fhir_base_url}/Patient", params={"_count": "1"})
    assert r.status_code == 200
    body = r.json()
    assert body["resourceType"] == "Bundle"


def test_coverage_search_returns_bundle(http, fhir_base_url):
    r = http.get(f"{fhir_base_url}/Coverage", params={"_count": "1"})
    assert r.status_code == 200
    body = r.json()
    assert body["resourceType"] == "Bundle"
