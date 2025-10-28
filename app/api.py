"""FastAPI entrypoint exposing the Gemini Data Analytics agent."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException
from google.api_core import exceptions as gcloud_exceptions
from google.protobuf.json_format import MessageToDict
from pydantic import BaseModel

from app.agent_service import create_or_update_agent, get_agent
from app.chat_service import scripted_chat
from app.config import Settings, load_settings

app = FastAPI(title="Analytics Data Agent", version="0.1.0")
_settings: Optional[Settings] = None


class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    preview: bool = False


class ChatResponse(BaseModel):
    conversation_id: str
    output: str


class AgentSyncResponse(BaseModel):
    name: str
    created: str
    updated: Optional[str]


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = load_settings(dotenv=False)
    return _settings


@app.get("/health", tags=["meta"])
def healthz() -> dict[str, str]:
    """Simple readiness probe."""
    return {"status": "ok"}


@app.get("/agent", tags=["agent"])
def read_agent():
    """Retrieve the currently configured data agent."""
    settings = get_settings()
    try:
        agent = get_agent(settings)
    except gcloud_exceptions.GoogleAPICallError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    return MessageToDict(agent.to_proto())


@app.post("/agent/sync", response_model=AgentSyncResponse, tags=["agent"])
def sync_agent():
    """Ensure the data agent exists and return its metadata."""
    settings = get_settings()
    try:
        agent = create_or_update_agent(settings)
    except gcloud_exceptions.GoogleAPICallError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return AgentSyncResponse(
        name=agent.name,
        created=str(agent.create_time),
        updated=str(agent.update_time) if agent.update_time else None,
    )


@app.post("/chat", response_model=ChatResponse, tags=["chat"])
def chat(request: ChatRequest) -> ChatResponse:
    """Send a question to the data agent and return the generated answer."""
    settings = get_settings()
    conversation_id = request.conversation_id or f"api-{uuid.uuid4().hex}"

    try:
        transcript = scripted_chat(
            settings,
            conversation_id,
            [request.question],
            enable_preview=request.preview,
            transcript_path=None,
        )
    except gcloud_exceptions.GoogleAPICallError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not transcript:
        raise HTTPException(status_code=500, detail="Empty transcript received")

    return ChatResponse(
        conversation_id=conversation_id,
        output=transcript[-1]["output"],
    )
