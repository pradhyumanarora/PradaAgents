"""
FastAPI backend for the Agentic Development Team.

Exposes the multi-agent team via REST + SSE endpoints.
Users interact through the UI to:
  - Submit tasks
  - Stream real-time agent messages
  - Manage MCP server configurations
  - Browse chat history (persisted in PostgreSQL)
"""

import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, update

from agentic_team.team import AgenticDevelopmentTeam
from agentic_team.mcp_integration import (
    MCP_SERVERS,
    MCPServerConfig,
    AGENT_MCP_MAPPING,
    _load_servers_from_yaml,
)
from backend.db import init_db, async_session, ChatSession, ChatMessage

# ---------------------------------------------------------------------------
# Lifespan — init DB on startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="PradaAgent Backend",
    description="Backend API for the Agentic Development Team",
    version="1.1.0",
    lifespan=lifespan,
)

ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory state
# ---------------------------------------------------------------------------

# Active task sessions: session_id -> { team, status, messages }
_sessions: Dict[str, dict] = {}

MCP_YAML_PATH = os.getenv(
    "MCP_SERVERS_CONFIG",
    str(Path(__file__).resolve().parent.parent / "mcp_servers.yaml"),
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class TaskRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=10000)
    model_name: str = "gpt-5.3-chat"
    max_iterations: int = Field(default=30, ge=1, le=100)
    azure_endpoint: Optional[str] = None
    azure_api_version: str = "2024-12-01-preview"


class MCPServerInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    server_type: str = Field(..., pattern=r"^(http|stdio)$")
    url: Optional[str] = None
    command: Optional[str] = None
    args: Optional[list] = None
    env: Optional[Dict[str, str]] = None


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Agents info
# ---------------------------------------------------------------------------

@app.get("/api/agents")
async def list_agents():
    """Return metadata about the available agents."""
    agents = [
        {
            "name": "ArchitectAgent",
            "description": "Designs system architecture and technical specifications",
            "mcp_servers": AGENT_MCP_MAPPING.get("ArchitectAgent", []),
        },
        {
            "name": "DeveloperAgent",
            "description": "Implements features and writes production code",
            "mcp_servers": AGENT_MCP_MAPPING.get("DeveloperAgent", []),
        },
        {
            "name": "CodeReviewerAgent",
            "description": "Reviews code quality and suggests improvements",
            "mcp_servers": AGENT_MCP_MAPPING.get("CodeReviewerAgent", []),
        },
        {
            "name": "SecurityAgent",
            "description": "Audits for vulnerabilities and security best practices",
            "mcp_servers": AGENT_MCP_MAPPING.get("SecurityAgent", []),
        },
        {
            "name": "PRReviewAgent",
            "description": "Manages Azure DevOps PRs, comments, and approvals",
            "mcp_servers": AGENT_MCP_MAPPING.get("PRReviewAgent", []),
        },
    ]
    return {"agents": agents}


# ---------------------------------------------------------------------------
# MCP Servers CRUD
# ---------------------------------------------------------------------------

def _read_yaml() -> dict:
    if Path(MCP_YAML_PATH).exists():
        with open(MCP_YAML_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def _write_yaml(data: dict):
    with open(MCP_YAML_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


@app.get("/api/mcp-servers")
async def list_mcp_servers():
    """List all configured MCP servers."""
    raw = _read_yaml()
    servers = []
    for name, cfg in raw.items():
        servers.append({"name": name, **cfg})
    return {"servers": servers}


@app.post("/api/mcp-servers", status_code=201)
async def add_mcp_server(server: MCPServerInput):
    """Add a new MCP server configuration."""
    raw = _read_yaml()
    if server.name in raw:
        raise HTTPException(status_code=409, detail=f"Server '{server.name}' already exists")

    entry: dict = {"type": server.server_type}
    if server.server_type == "http":
        if not server.url:
            raise HTTPException(status_code=422, detail="HTTP servers require a 'url'")
        entry["url"] = server.url
    else:
        if not server.command:
            raise HTTPException(status_code=422, detail="stdio servers require a 'command'")
        entry["command"] = server.command
        if server.args:
            entry["args"] = server.args
    if server.env:
        entry["env"] = server.env

    raw[server.name] = entry
    _write_yaml(raw)
    return {"message": f"Server '{server.name}' added", "server": {"name": server.name, **entry}}


@app.put("/api/mcp-servers/{name}")
async def update_mcp_server(name: str, server: MCPServerInput):
    """Update an existing MCP server configuration."""
    raw = _read_yaml()
    if name not in raw:
        raise HTTPException(status_code=404, detail=f"Server '{name}' not found")

    entry: dict = {"type": server.server_type}
    if server.server_type == "http":
        if not server.url:
            raise HTTPException(status_code=422, detail="HTTP servers require a 'url'")
        entry["url"] = server.url
    else:
        if not server.command:
            raise HTTPException(status_code=422, detail="stdio servers require a 'command'")
        entry["command"] = server.command
        if server.args:
            entry["args"] = server.args
    if server.env:
        entry["env"] = server.env

    # If name changed, remove old key
    if name != server.name:
        del raw[name]
    raw[server.name] = entry
    _write_yaml(raw)
    return {"message": f"Server '{server.name}' updated", "server": {"name": server.name, **entry}}


@app.delete("/api/mcp-servers/{name}")
async def delete_mcp_server(name: str):
    """Remove an MCP server configuration."""
    raw = _read_yaml()
    if name not in raw:
        raise HTTPException(status_code=404, detail=f"Server '{name}' not found")
    del raw[name]
    _write_yaml(raw)
    return {"message": f"Server '{name}' deleted"}


# ---------------------------------------------------------------------------
# Task execution with SSE streaming
# ---------------------------------------------------------------------------

@app.get("/api/model-config")
async def get_model_config():
    """Return current model configuration derived from env vars."""
    azure_ep = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    return {
        "is_azure": bool(azure_ep),
        "azure_endpoint": azure_ep,
        "azure_api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        "default_model": os.getenv("OPENAI_MODEL", "gpt-5.3-chat"),
    }


@app.post("/api/tasks")
async def start_task(req: TaskRequest):
    """Start a new task — persisted to DB."""
    session_id = uuid.uuid4().hex
    # In-memory entry for the running stream
    _sessions[session_id] = {
        "status": "pending",
        "messages": [],
        "task": req.task,
        "model_name": req.model_name,
        "max_iterations": req.max_iterations,
        "azure_endpoint": req.azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        "azure_api_version": req.azure_api_version,
    }
    # Persist to DB
    async with async_session() as db:
        db.add(ChatSession(
            id=session_id,
            task=req.task,
            model_name=req.model_name,
            max_iterations=req.max_iterations,
            status="pending",
        ))
        await db.commit()
    return {"session_id": session_id}


@app.get("/api/tasks/{session_id}/stream")
async def stream_task(session_id: str):
    """SSE endpoint – runs agents and streams + persists each message."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["status"] == "running":
        raise HTTPException(status_code=409, detail="Task already running")

    session["status"] = "running"
    session["_cancel"] = False

    async def event_generator():
        seq = len(session["messages"])
        azure_ep = session.get("azure_endpoint", "")
        team = AgenticDevelopmentTeam(
            model_name=session["model_name"],
            max_iterations=session["max_iterations"],
            azure_endpoint=azure_ep if azure_ep else None,
            azure_api_version=session.get("azure_api_version", "2024-12-01-preview"),
        )

        # Mark running in DB
        async with async_session() as db:
            await db.execute(
                update(ChatSession).where(ChatSession.id == session_id).values(status="running")
            )
            await db.commit()

        try:
            stream = team.team.run_stream(task=session["task"])
            async for message in stream:
                # Check for cancellation
                if session.get("_cancel"):
                    break

                source = getattr(message, "source", "system")
                content = getattr(message, "content", str(message))
                msg_type = type(message).__name__

                payload = {"source": source, "content": content, "type": msg_type}
                session["messages"].append(payload)
                seq += 1

                # Persist message
                async with async_session() as db:
                    db.add(ChatMessage(
                        session_id=session_id, seq=seq,
                        source=source, content=content if isinstance(content, str) else str(content),
                        msg_type=msg_type,
                    ))
                    await db.commit()

                yield f"data: {json.dumps(payload)}\n\n"

            final_status = "stopped" if session.get("_cancel") else "completed"
            session["status"] = final_status
            async with async_session() as db:
                await db.execute(
                    update(ChatSession).where(ChatSession.id == session_id).values(status=final_status)
                )
                await db.commit()
            yield f"data: {json.dumps({'type': 'done', 'source': 'system', 'content': 'Task ' + final_status})}\n\n"

        except Exception as exc:
            session["status"] = "error"
            async with async_session() as db:
                await db.execute(
                    update(ChatSession).where(ChatSession.id == session_id).values(status="error")
                )
                await db.commit()
            yield f"data: {json.dumps({'type': 'error', 'source': 'system', 'content': str(exc)})}\n\n"
        finally:
            await team.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/tasks/{session_id}")
async def get_task_status(session_id: str):
    """Get task status and messages — falls back to DB if not in memory."""
    # Try in-memory first (active session)
    session = _sessions.get(session_id)
    if session:
        return {
            "session_id": session_id,
            "status": session["status"],
            "task": session["task"],
            "message_count": len(session["messages"]),
            "messages": session["messages"],
        }
    # Fall back to DB (historical)
    async with async_session() as db:
        result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
        chat = result.scalar_one_or_none()
        if not chat:
            raise HTTPException(status_code=404, detail="Session not found")
        msg_result = await db.execute(
            select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.seq)
        )
        msgs = [{"source": m.source, "content": m.content, "type": m.msg_type} for m in msg_result.scalars()]
    return {
        "session_id": session_id,
        "status": chat.status,
        "task": chat.task,
        "model_name": chat.model_name,
        "created_at": chat.created_at.isoformat() if chat.created_at else None,
        "message_count": len(msgs),
        "messages": msgs,
    }


# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------

@app.get("/api/history")
async def list_history():
    """List all past chat sessions (newest first)."""
    async with async_session() as db:
        result = await db.execute(
            select(ChatSession).order_by(ChatSession.created_at.desc()).limit(50)
        )
        sessions = result.scalars().all()
    return {
        "sessions": [
            {
                "id": s.id,
                "task": s.task[:120],
                "status": s.status,
                "model_name": s.model_name,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in sessions
        ]
    }


# ---------------------------------------------------------------------------
# Stop a running task
# ---------------------------------------------------------------------------

@app.post("/api/tasks/{session_id}/stop")
async def stop_task(session_id: str):
    """Signal a running task to stop."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["status"] != "running":
        raise HTTPException(status_code=409, detail="Task is not running")
    session["_cancel"] = True
    return {"message": "Stop signal sent"}


# ---------------------------------------------------------------------------
# Follow-up: continue a session with a new prompt
# ---------------------------------------------------------------------------

class FollowUpRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)


@app.post("/api/tasks/{session_id}/followup")
async def followup_task(session_id: str, req: FollowUpRequest):
    """
    Continue an existing session with a new user prompt.
    Builds a combined task from the history + new prompt so agents have full context.
    Returns a new session_id for the follow-up stream.
    """
    # Load history from memory or DB
    session = _sessions.get(session_id)
    if session:
        prev_messages = session["messages"]
        model_name = session["model_name"]
        max_iter = session["max_iterations"]
        azure_ep = session.get("azure_endpoint", "")
        azure_ver = session.get("azure_api_version", "2024-12-01-preview")
        original_task = session["task"]
    else:
        async with async_session() as db:
            result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
            chat = result.scalar_one_or_none()
            if not chat:
                raise HTTPException(status_code=404, detail="Session not found")
            msg_result = await db.execute(
                select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.seq)
            )
            prev_messages = [{"source": m.source, "content": m.content, "type": m.msg_type} for m in msg_result.scalars()]
            model_name = chat.model_name
            max_iter = chat.max_iterations
            azure_ep = os.getenv("AZURE_OPENAI_ENDPOINT", "")
            azure_ver = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
            original_task = chat.task

    # Build combined task with conversation history summary
    history_text = "\n".join(
        f"[{m['source']}]: {m['content'][:500]}" for m in prev_messages if m.get("content")
    )
    combined_task = f"""## Previous conversation context:
{history_text}

## New instruction from the user:
{req.prompt}

Continue working based on the above conversation history and the new instruction. Do NOT repeat work already done."""

    # Create new session for the follow-up
    new_id = uuid.uuid4().hex
    _sessions[new_id] = {
        "status": "pending",
        "messages": list(prev_messages),  # carry forward old messages
        "task": combined_task,
        "model_name": model_name,
        "max_iterations": max_iter,
        "azure_endpoint": azure_ep,
        "azure_api_version": azure_ver,
    }

    async with async_session() as db:
        db.add(ChatSession(
            id=new_id,
            task=f"[Follow-up] {req.prompt[:200]}",
            model_name=model_name,
            max_iterations=max_iter,
            status="pending",
        ))
        # Persist carried-forward messages
        for i, m in enumerate(prev_messages, 1):
            db.add(ChatMessage(
                session_id=new_id, seq=i,
                source=m["source"],
                content=m["content"] if isinstance(m["content"], str) else str(m["content"]),
                msg_type=m.get("type", "TextMessage"),
            ))
        await db.commit()

    return {"session_id": new_id}
