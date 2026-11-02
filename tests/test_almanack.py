"""
Smoke tests for Poor Richard's Engineering Almanack.
In-cluster URL: http://almanack.almanack:8000
"""

import os
import re

import pytest

BASE_URL = os.getenv("ALMANACK_BASE_URL", "http://almanack.almanack:8000")


@pytest.fixture
def almanack_url():
    return BASE_URL


def test_health(http, almanack_url):
    r = http.get(f"{almanack_url}/health")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "ok"
    assert isinstance(body.get("sayings_loaded"), int)
    assert body["sayings_loaded"] > 0, "No sayings loaded — run corpus ingestion"


def test_random_returns_saying(http, almanack_url):
    r = http.get(f"{almanack_url}/random")
    assert r.status_code == 200
    body = r.json()
    assert "text" in body
    assert isinstance(body["text"], str)
    assert len(body["text"]) > 10, "Random saying text is suspiciously short"


def test_ask_returns_answer_and_sayings(http, almanack_url):
    r = http.post(
        f"{almanack_url}/ask",
        json={"question": "Should I ship quickly or test more thoroughly?"},
        timeout=90,
    )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    body = r.json()
    assert "answer" in body, "Response missing 'answer' field"
    assert "sayings" in body, "Response missing 'sayings' field"
    assert isinstance(body["answer"], str)
    assert len(body["answer"]) > 20, "Answer is suspiciously short"
    assert isinstance(body["sayings"], list)


def test_ask_quotes_verify(http, almanack_url):
    """
    Every double-quoted string in the answer must appear verbatim in the
    returned sayings. This is the anti-hallucination guardrail.
    """
    r = http.post(
        f"{almanack_url}/ask",
        json={"question": "How should I handle technical debt?"},
        timeout=90,
    )
    assert r.status_code == 200
    body = r.json()
    answer  = body["answer"]
    sayings = [s["text"] for s in body.get("sayings", [])]

    quoted = re.findall(r'"([^"]{10,})"', answer)
    for q in quoted:
        assert any(q in t for t in sayings), (
            f"Quoted string not found in retrieved sayings.\n"
            f"Quote: {q!r}\n"
            f"Sayings: {sayings}"
        )


def test_ask_rejects_empty_question(http, almanack_url):
    r = http.post(f"{almanack_url}/ask", json={"question": ""})
    assert r.status_code == 422


def test_ask_rejects_overlong_question(http, almanack_url):
    r = http.post(f"{almanack_url}/ask", json={"question": "x" * 501})
    assert r.status_code == 422
