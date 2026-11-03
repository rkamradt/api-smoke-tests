"""
Smoke tests for the Home Assistant voice stack.

In-cluster URLs (all in home-assistant namespace):
  Home Assistant : http://home-assistant.home-assistant:8123
  Whisper (STT)  : wyoming-whisper.home-assistant:10300  (TCP)
  Piper (TTS)    : wyoming-piper.home-assistant:10200    (TCP)
  openWakeWord   : wyoming-openwakeword.home-assistant:10400 (TCP, optional)
"""
import os
import socket

import pytest

HA_BASE_URL = os.getenv("HA_BASE_URL", "http://home-assistant.home-assistant:8123")
WHISPER_HOST = os.getenv("WHISPER_HOST", "wyoming-whisper.home-assistant")
WHISPER_PORT = int(os.getenv("WHISPER_PORT", "10300"))
PIPER_HOST = os.getenv("PIPER_HOST", "wyoming-piper.home-assistant")
PIPER_PORT = int(os.getenv("PIPER_PORT", "10200"))
OWW_HOST = os.getenv("OWW_HOST", "wyoming-openwakeword.home-assistant")
OWW_PORT = int(os.getenv("OWW_PORT", "10400"))
OWW_ENABLED = os.getenv("OWW_ENABLED", "true").lower() == "true"

TIMEOUT = float(os.getenv("SMOKE_TIMEOUT", "15"))


def _tcp_ok(host: str, port: int) -> None:
    """Assert that a TCP connection to host:port succeeds."""
    with socket.create_connection((host, port), timeout=TIMEOUT):
        pass


def test_home_assistant_http(http):
    """HA is up — root returns 200 (onboarding) or 302 (redirect to login)."""
    r = http.get(f"{HA_BASE_URL}/")
    assert r.status_code in (200, 302), f"Expected 200 or 302, got {r.status_code}"


def test_whisper_wyoming_port():
    """Whisper Wyoming TCP port is accepting connections."""
    _tcp_ok(WHISPER_HOST, WHISPER_PORT)


def test_piper_wyoming_port():
    """Piper Wyoming TCP port is accepting connections."""
    _tcp_ok(PIPER_HOST, PIPER_PORT)


def test_openwakeword_wyoming_port():
    """openWakeWord Wyoming TCP port is accepting connections (skipped if disabled)."""
    if not OWW_ENABLED:
        pytest.skip("openWakeWord disabled (OWW_ENABLED=false)")
    _tcp_ok(OWW_HOST, OWW_PORT)
