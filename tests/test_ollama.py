"""
Smoke tests for Ollama LLM server.
In-cluster URL: http://ollama.llm.svc.cluster.local:11434
"""
import os

EXPECTED_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b-instruct-q4_K_M")


def test_list_models(http, ollama_base_url):
    r = http.get(f"{ollama_base_url}/api/tags")
    assert r.status_code == 200
    body = r.json()
    assert "models" in body


def test_expected_model_loaded(http, ollama_base_url):
    r = http.get(f"{ollama_base_url}/api/tags")
    assert r.status_code == 200
    names = [m["name"] for m in r.json().get("models", [])]
    assert any(EXPECTED_MODEL in name for name in names), (
        f"{EXPECTED_MODEL} not found in loaded models: {names}"
    )


def test_generate_short_response(http, ollama_base_url):
    payload = {
        "model": EXPECTED_MODEL,
        "prompt": "Reply with only the word: pong",
        "stream": False,
    }
    r = http.post(f"{ollama_base_url}/api/generate", json=payload, timeout=60)
    assert r.status_code == 200
    body = r.json()
    assert "response" in body
    assert len(body["response"]) > 0
