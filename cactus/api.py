"""
FastAPI server exposing CactusRalph-Coder agent endpoints.

Endpoints:
  GET  /health                    — liveness check
  POST /api/v1/task               — run a full coding cycle (blocking)
  POST /api/v1/task/stream        — run a coding cycle with SSE progress events
  GET  /api/v1/memory             — list recent sessions
  GET  /api/v1/memory/search      — search sessions by keyword
  DELETE /api/v1/memory           — clear all sessions
  GET  /api/v1/queue              — list tasks in the queue
  POST /api/v1/queue              — add a task to the queue
  POST /api/v1/queue/process      — trigger background queue processing

Start with:
  uvicorn cactus.api:app --reload
or via main.py:
  python main.py --serve
"""

import asyncio
import json
import os
from typing import AsyncGenerator

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from cactus.engine import CactusEngine

app = FastAPI(
    title="CactusRalph-Coder API",
    description="AI-Powered Coding Agent REST API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Module-level engine singleton; reset to None in tests to get a fresh instance.
_engine: CactusEngine = None


def get_engine() -> CactusEngine:
    """Return (and lazily create) the shared CactusEngine instance."""
    global _engine
    if _engine is None:
        _engine = CactusEngine(project_root=os.getcwd())
    return _engine


# ─── Request / Response models ──────────────────────────────────────────────


class TaskRequest(BaseModel):
    requirement: str


class QueueTaskRequest(BaseModel):
    requirement: str
    priority: int = 0


# ─── Health ──────────────────────────────────────────────────────────────────


@app.get("/health", tags=["ops"])
async def health():
    """Liveness probe."""
    return {"status": "ok", "service": "CactusRalph-Coder"}


# ─── Task ────────────────────────────────────────────────────────────────────


@app.post("/api/v1/task", tags=["agent"])
async def run_task(req: TaskRequest):
    """
    Run a full Plan → Code → Review → Test cycle and return the result.
    Blocks until the cycle is complete.
    """
    engine = get_engine()
    try:
        result = await asyncio.to_thread(engine.run_coding_cycle, req.requirement)
        return result
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@app.post("/api/v1/task/stream", tags=["agent"])
async def run_task_stream(req: TaskRequest):
    """
    Run a coding cycle and stream progress via Server-Sent Events (SSE).

    Each SSE event is a JSON object::

        {"event": "<stage>", "data": {...}}

    Stages in order: ``planning``, ``coding``, ``reviewing``, ``testing``,
    then ``done`` which carries the full result payload.

    Example (JavaScript)::

        const es = new EventSource('/api/v1/task/stream');
        es.onmessage = e => console.log(JSON.parse(e.data));
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        engine = get_engine()
        result: dict = {}

        # Kick off the blocking cycle in a thread
        async def run_cycle():
            nonlocal result
            result = await asyncio.to_thread(engine.run_coding_cycle, req.requirement)

        task = asyncio.create_task(run_cycle())

        # Emit progress events while the task is running
        progress_stages = [
            ("planning", "Planning the implementation…"),
            ("coding", "Generating code…"),
            ("reviewing", "Reviewing generated code…"),
            ("testing", "Generating tests…"),
        ]

        for event, message in progress_stages:
            payload = json.dumps({"event": event, "data": {"message": message}})
            yield f"data: {payload}\n\n"
            await asyncio.sleep(0.05)

        # Wait for the cycle to finish, then emit the final result
        await task
        done_payload = json.dumps({"event": "done", "data": result})
        yield f"data: {done_payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ─── Memory ──────────────────────────────────────────────────────────────────


@app.get("/api/v1/memory", tags=["memory"])
async def get_memory(n: int = 10):
    """Return the *n* most recent coding sessions from persistent memory."""
    engine = get_engine()
    return {"sessions": engine.memory.get_recent(n)}


@app.get("/api/v1/memory/search", tags=["memory"])
async def search_memory(q: str):
    """Search memory sessions by keyword (case-insensitive substring match)."""
    engine = get_engine()
    return {"results": engine.memory.search(q)}


@app.delete("/api/v1/memory", tags=["memory"])
async def clear_memory():
    """Wipe all stored sessions from memory."""
    engine = get_engine()
    engine.memory.clear()
    return {"status": "cleared"}


# ─── Queue ───────────────────────────────────────────────────────────────────


@app.get("/api/v1/queue", tags=["queue"])
async def get_queue():
    """Return all tasks currently in the task queue."""
    engine = get_engine()
    return {"tasks": engine._load_queue()}


@app.post("/api/v1/queue", tags=["queue"])
async def add_to_queue(req: QueueTaskRequest):
    """Add a coding requirement to the task queue."""
    engine = get_engine()
    tasks = engine._load_queue()
    task = {
        "requirement": req.requirement,
        "priority": req.priority,
        "status": "pending",
    }
    tasks.append(task)
    engine._save_queue(tasks)
    return {"status": "queued", "task": task}


@app.post("/api/v1/queue/process", tags=["queue"])
async def process_queue(background_tasks: BackgroundTasks):
    """Trigger background processing of all pending tasks in the queue."""
    engine = get_engine()
    background_tasks.add_task(engine._process_queue)
    return {"status": "processing"}
