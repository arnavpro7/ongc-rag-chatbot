"""
test_backend.py
----------------
Test suite for the FastAPI backend.

HOW TO RUN:
    cd backend
    pip install -r requirements.txt
    pytest ../tests/test_backend.py -v

These tests use FastAPI's TestClient, which calls the app in-process
(no real network needed) and monkeypatches the outbound Ollama calls,
so the suite works even if Ollama is not installed.

For interns: notice the pattern in every test —
1. Arrange (set up fake data / mocks)
2. Act (call the endpoint)
3. Assert (check the response)
"""

import sys
import os
import pytest
from unittest.mock import AsyncMock, patch
import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient
import main as backend_main  # noqa: E402

# Using TestClient as a context manager triggers FastAPI's startup/shutdown
# lifespan events, which is what creates backend_main.http_client.
_client_cm = TestClient(backend_main.app)
client = _client_cm.__enter__()


def _close_client():
    _client_cm.__exit__(None, None, None)


import atexit  # noqa: E402
atexit.register(_close_client)


@pytest.fixture(autouse=True)
def clear_conversations():
    """Reset in-memory history before every test so tests don't leak state."""
    backend_main.conversations.clear()
    yield
    backend_main.conversations.clear()


def _fake_ollama_response(reply_text="Hello! How can I help you today?"):
    """Build a fake httpx.Response shaped like Ollama's /api/chat reply."""
    return httpx.Response(
        status_code=200,
        json={"message": {"role": "assistant", "content": reply_text}},
        request=httpx.Request("POST", "http://fake/api/chat"),
    )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
def test_health_check_reports_backend_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["backend_status"] == "ok"


# ---------------------------------------------------------------------------
# Valid chat request
# ---------------------------------------------------------------------------
def test_valid_chat_request_returns_reply():
    with patch.object(backend_main.http_client, "post", new=AsyncMock(return_value=_fake_ollama_response())):
        response = client.post("/chat", json={"session_id": "test-1", "message": "Hi there"})
    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == "test-1"
    assert body["reply"] == "Hello! How can I help you today?"
    assert body["history_length"] >= 2  # system + user (+ assistant)


# ---------------------------------------------------------------------------
# Empty message
# ---------------------------------------------------------------------------
def test_empty_message_is_rejected():
    response = client.post("/chat", json={"session_id": "test-2", "message": ""})
    # Pydantic's min_length=1 rejects this before it reaches our handler
    assert response.status_code == 422


def test_whitespace_only_message_is_rejected():
    response = client.post("/chat", json={"session_id": "test-2b", "message": "   "})
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Very long message
# ---------------------------------------------------------------------------
def test_overly_long_message_is_rejected():
    huge_message = "a" * 5000  # over the 4000-char limit in schemas.py
    response = client.post("/chat", json={"session_id": "test-3", "message": huge_message})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Invalid requests
# ---------------------------------------------------------------------------
def test_missing_session_id_is_rejected():
    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 422


def test_malformed_json_is_rejected():
    response = client.post(
        "/chat", data="not json", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Ollama unavailable
# ---------------------------------------------------------------------------
def test_ollama_connection_refused_returns_503():
    with patch.object(
        backend_main.http_client, "post",
        new=AsyncMock(side_effect=httpx.ConnectError("connection refused")),
    ):
        response = client.post("/chat", json={"session_id": "test-4", "message": "hi"})
    assert response.status_code == 503
    assert "Ollama" in response.json()["detail"]


# ---------------------------------------------------------------------------
# Slow response / timeout
# ---------------------------------------------------------------------------
def test_ollama_timeout_returns_504():
    with patch.object(
        backend_main.http_client, "post",
        new=AsyncMock(side_effect=httpx.TimeoutException("timed out")),
    ):
        response = client.post("/chat", json={"session_id": "test-5", "message": "hi"})
    assert response.status_code == 504


# ---------------------------------------------------------------------------
# Model not found on the Ollama server
# ---------------------------------------------------------------------------
def test_model_not_found_returns_404():
    not_found_response = httpx.Response(
        status_code=404, text="model not found",
        request=httpx.Request("POST", "http://fake/api/chat"),
    )
    with patch.object(backend_main.http_client, "post", new=AsyncMock(return_value=not_found_response)):
        response = client.post("/chat", json={"session_id": "test-6", "message": "hi"})
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Multi-turn conversation behavior
# ---------------------------------------------------------------------------
def test_multi_turn_conversation_keeps_history():
    with patch.object(backend_main.http_client, "post", new=AsyncMock(return_value=_fake_ollama_response("Reply 1"))):
        client.post("/chat", json={"session_id": "test-7", "message": "First message"})
    with patch.object(backend_main.http_client, "post", new=AsyncMock(return_value=_fake_ollama_response("Reply 2"))):
        response = client.post("/chat", json={"session_id": "test-7", "message": "Second message"})

    assert response.status_code == 200
    # system + user1 + assistant1 + user2 + assistant2 = 5
    assert response.json()["history_length"] == 5

    history_response = client.get("/conversations/test-7")
    contents = [m["content"] for m in history_response.json()["messages"]]
    assert "First message" in contents
    assert "Second message" in contents


def test_clear_conversation_resets_history():
    with patch.object(backend_main.http_client, "post", new=AsyncMock(return_value=_fake_ollama_response())):
        client.post("/chat", json={"session_id": "test-8", "message": "hello"})

    delete_response = client.delete("/conversations/test-8")
    assert delete_response.status_code == 200

    history_response = client.get("/conversations/test-8")
    # Only the re-seeded system prompt should remain
    assert len(history_response.json()["messages"]) == 1


def test_get_conversation_for_unknown_session_returns_404():
    response = client.get("/conversations/does-not-exist")
    assert response.status_code == 404
