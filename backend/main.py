"""
main.py
-------
A small, beginner-friendly FastAPI backend that sits between a client
(a browser, a script, or Open WebUI's "OpenAI-compatible" client) and
a local Ollama server.

WHY DOES THIS EXIST if Open WebUI already talks to Ollama directly?
This backend is OPTIONAL. It exists purely for internship learning value:
- Shows interns how to call the Ollama HTTP API from Python.
- Shows request validation, error handling, env-based config.
- Shows how to keep server-side conversation history.
- Gives interns a real FastAPI service to extend (auth, logging, RAG, etc.)

Run it with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Then open http://localhost:8000/docs for interactive API docs.
"""

import os
import time
import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from schemas import (
    ChatRequest, ChatResponse, HealthResponse,
    ConversationResponse, Message, Role,
)

# ---------------------------------------------------------------------------
# Configuration (loaded from environment variables / .env file)
# ---------------------------------------------------------------------------
load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2:3b")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")

SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    (
        "You are an internal training assistant for new interns. "
        "Answer clearly, accurately, and step by step. "
        "If you do not know something, say so instead of guessing. "
        "Never invent facts, numbers, or sources. "
        "If a request is ambiguous, ask a clarifying question before answering. "
        "Never provide harmful, illegal, or unsafe instructions. "
        "Never ask for or repeat back passwords, API keys, or confidential data."
    ),
)

# ---------------------------------------------------------------------------
# Logging (basic — never log full message content in a real deployment
# if it might contain sensitive data; here we log only metadata)
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chatbot-backend")

# ---------------------------------------------------------------------------
# In-memory conversation store.
# NOTE for interns: this is intentionally simple. It resets when the
# server restarts and is NOT shared across multiple backend replicas.
# A production version would use Redis or a database instead.
# ---------------------------------------------------------------------------
conversations: dict[str, list[Message]] = {}

# Shared HTTP client, created once at startup and reused (more efficient
# than opening a new connection for every request).
http_client: httpx.AsyncClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    http_client = httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS)
    logger.info(f"Backend starting. Ollama URL: {OLLAMA_BASE_URL}, Model: {MODEL_NAME}")
    yield
    await http_client.aclose()
    logger.info("Backend shutting down.")


app = FastAPI(
    title="Local LLM Chatbot Backend",
    description="Educational FastAPI backend that proxies chat requests to a local Ollama server.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: allows a browser-based frontend on a different port/origin to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def get_or_create_history(session_id: str) -> list[Message]:
    """Return the message history for a session, creating it (with the
    system prompt as the first message) if it doesn't exist yet."""
    if session_id not in conversations:
        conversations[session_id] = [Message(role=Role.system, content=SYSTEM_PROMPT)]
    return conversations[session_id]


def trim_history(history: list[Message]) -> list[Message]:
    """Keep the system prompt plus only the most recent N turns, so the
    request sent to the model doesn't grow without bound."""
    system_msg = history[0]
    recent = history[1:][-MAX_HISTORY_MESSAGES:]
    return [system_msg] + recent


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health-check endpoint.

    Checks:
    1. Is the backend itself running? (if this returns anything, yes)
    2. Can the backend reach Ollama?
    """
    ollama_status = "unreachable"
    try:
        resp = await http_client.get(f"{OLLAMA_BASE_URL}/api/tags")
        ollama_status = "ok" if resp.status_code == 200 else f"error ({resp.status_code})"
    except httpx.ConnectError:
        ollama_status = "connection_refused"
    except httpx.TimeoutException:
        ollama_status = "timeout"
    except Exception as exc:  # noqa: BLE001 - deliberately broad for a health check
        ollama_status = f"error: {exc}"

    return HealthResponse(
        backend_status="ok",
        ollama_status=ollama_status,
        ollama_url=OLLAMA_BASE_URL,
        model_configured=MODEL_NAME,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.

    Flow:
    1. Validate input (handled automatically by ChatRequest / Pydantic).
    2. Load (or create) this session's history.
    3. Append the new user message.
    4. Call Ollama's /api/chat endpoint with the full message list.
    5. Append the assistant's reply to history and return it.
    """
    message_text = request.message.strip()
    if not message_text:
        raise HTTPException(status_code=400, detail="Message cannot be empty or whitespace only.")

    history = get_or_create_history(request.session_id)
    history.append(Message(role=Role.user, content=message_text))
    history = trim_history(history)
    conversations[request.session_id] = history

    ollama_payload = {
        "model": MODEL_NAME,
        "messages": [m.model_dump() for m in history],
        "stream": False,
    }

    try:
        response = await http_client.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=ollama_payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Could not connect to Ollama. Is it running? "
                f"Backend is trying to reach: {OLLAMA_BASE_URL}"
            ),
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail=f"Ollama did not respond within {REQUEST_TIMEOUT_SECONDS} seconds.",
        )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Error contacting Ollama: {exc}")

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Model '{MODEL_NAME}' not found on the Ollama server. "
                f"Pull it first with: ollama pull {MODEL_NAME}"
            ),
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama returned an unexpected status: {response.status_code} - {response.text}",
        )

    try:
        data = response.json()
        reply_text = data["message"]["content"]
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=f"Unexpected response format from Ollama: {exc}")

    history.append(Message(role=Role.assistant, content=reply_text))
    conversations[request.session_id] = history

    return ChatResponse(
        session_id=request.session_id,
        reply=reply_text,
        model=MODEL_NAME,
        history_length=len(history),
    )


@app.get("/conversations/{session_id}", response_model=ConversationResponse)
async def get_conversation(session_id: str):
    """Return the stored message history for a session (useful for debugging/UI)."""
    if session_id not in conversations:
        raise HTTPException(status_code=404, detail="No conversation found for this session_id.")
    return ConversationResponse(session_id=session_id, messages=conversations[session_id])


@app.delete("/conversations/{session_id}")
async def clear_conversation(session_id: str):
    """Clear a session's history (starts a fresh conversation, keeps system prompt)."""
    conversations.pop(session_id, None)
    get_or_create_history(session_id)  # re-seed with system prompt
    return {"status": "cleared", "session_id": session_id}


@app.get("/")
async def root():
    return {
        "service": "Local LLM Chatbot Backend",
        "docs": "/docs",
        "health": "/health",
    }
