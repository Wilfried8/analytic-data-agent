"""FastAPI entrypoint exposing the Gemini Data Analytics agent."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, Response
from google.api_core import exceptions as gcloud_exceptions
from google.protobuf.json_format import MessageToDict
from pydantic import BaseModel

from app.agent_service import create_agent, delete_agent, get_agent, list_agents, update_agent
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
    answer: str
    generated_sql: Optional[str] = None


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

    proto_agent = agent._pb if hasattr(agent, "_pb") else agent
    return MessageToDict(proto_agent)


@app.get("/agents", tags=["agent"])
def list_agents_endpoint():
    """List available data agents in the configured project/location."""
    settings = get_settings()
    try:
        agents = list_agents(settings)
    except gcloud_exceptions.GoogleAPICallError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    serialized_agents: list[dict[str, object]] = []
    for agent in agents:
        proto_agent = agent._pb if hasattr(agent, "_pb") else agent
        serialized_agents.append(MessageToDict(proto_agent))
    return serialized_agents


@app.post("/agent", response_model=AgentSyncResponse, tags=["agent"], status_code=201)
def create_agent_endpoint():
    """Create the data agent and return its metadata."""
    settings = get_settings()
    try:
        agent = create_agent(settings)
    except gcloud_exceptions.AlreadyExists as exc:
        raise HTTPException(status_code=409, detail="Agent already exists") from exc
    except gcloud_exceptions.GoogleAPICallError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return AgentSyncResponse(
        name=agent.name,
        created=str(agent.create_time),
        updated=str(agent.update_time) if agent.update_time else None,
    )


@app.put("/agent", response_model=AgentSyncResponse, tags=["agent"])
def update_agent_endpoint():
    """Update the data agent definition and return its metadata."""
    settings = get_settings()
    try:
        agent = update_agent(settings)
    except gcloud_exceptions.NotFound as exc:
        raise HTTPException(status_code=404, detail="Agent not found") from exc
    except gcloud_exceptions.GoogleAPICallError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return AgentSyncResponse(
        name=agent.name,
        created=str(agent.create_time),
        updated=str(agent.update_time) if agent.update_time else None,
    )


@app.delete("/agent/{agent_id}", tags=["agent"], status_code=204)
def delete_agent_endpoint(agent_id: str, force: bool = False):
    """Delete the specified data agent."""
    settings = get_settings()
    try:
        deleted = delete_agent(settings, agent_id=agent_id, force=force)
    except gcloud_exceptions.GoogleAPICallError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")

    return Response(status_code=204)


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

    turn = transcript[-1]
    answer = turn.get("answer", "").strip()
    if not answer:
        raise HTTPException(status_code=500, detail="No textual answer produced")

    return ChatResponse(
        conversation_id=conversation_id,
        answer=answer,
        generated_sql=turn.get("generated_sql"),
    )
