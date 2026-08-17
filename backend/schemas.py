"""
schemas.py
----------
Pydantic models (data "shapes") used by the FastAPI backend.

Interns: think of these as contracts. FastAPI uses them to:
1. Validate incoming JSON automatically (bad input -> automatic 422 error).
2. Generate the interactive API docs at /docs.
3. Give you editor autocomplete when you write code that uses them.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class Role(str, Enum):
    """Who sent a message in the conversation."""
    system = "system"
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    """A single message inside a conversation."""
    role: Role
    content: str


class ChatRequest(BaseModel):
    """
    What the frontend/client must send to POST /chat.

    session_id groups messages into one ongoing conversation, so the
    backend can remember earlier turns (multi-turn chat).
    """
    session_id: str = Field(
        ..., min_length=1, max_length=100,
        description="Unique ID for this conversation, e.g. a UUID."
    )
    message: str = Field(
        ..., min_length=1, max_length=4000,
        description="The user's message. Empty or overly long messages are rejected."
    )


class ChatResponse(BaseModel):
    """What the backend sends back after a successful chat call."""
    session_id: str
    reply: str
    model: str
    history_length: int


class HealthResponse(BaseModel):
    """Response shape for GET /health."""
    model_config = {"protected_namespaces": ()}

    backend_status: str
    ollama_status: str
    ollama_url: str
    model_configured: str


class ConversationResponse(BaseModel):
    """Response shape for GET /conversations/{session_id}."""
    session_id: str
    messages: List[Message]


class ErrorResponse(BaseModel):
    """Consistent error shape returned to clients on failure."""
    error: str
    detail: Optional[str] = None
