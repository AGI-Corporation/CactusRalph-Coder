"""
Tests for the CactusRalph-Coder FastAPI endpoints.

Uses FastAPI's TestClient — no real LLM calls, no network required.
The engine singleton is reset between tests via monkeypatch so each
test gets a clean in-memory state.
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import cactus.api as api_module
from cactus.api import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reset_engine(monkeypatch, tmp_path):
    """Point the engine at tmp_path and reset the singleton."""
    monkeypatch.setenv("MEMORY_FILE", str(tmp_path / "mem.json"))
    monkeypatch.setenv("TASK_QUEUE_FILE", str(tmp_path / "queue.json"))
    api_module._engine = None


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "CactusRalph" in data["service"]


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------


def test_get_memory_empty(tmp_path, monkeypatch):
    _reset_engine(monkeypatch, tmp_path)
    resp = client.get("/api/v1/memory")
    assert resp.status_code == 200
    assert resp.json()["sessions"] == []


def test_get_memory_with_limit(tmp_path, monkeypatch):
    _reset_engine(monkeypatch, tmp_path)
    resp = client.get("/api/v1/memory?n=5")
    assert resp.status_code == 200
    assert isinstance(resp.json()["sessions"], list)


def test_search_memory_empty(tmp_path, monkeypatch):
    _reset_engine(monkeypatch, tmp_path)
    resp = client.get("/api/v1/memory/search?q=fastapi")
    assert resp.status_code == 200
    assert resp.json()["results"] == []


def test_clear_memory(tmp_path, monkeypatch):
    _reset_engine(monkeypatch, tmp_path)
    resp = client.delete("/api/v1/memory")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cleared"


def test_memory_round_trip(tmp_path, monkeypatch):
    """Save a session via the Memory object and read it back via the API."""
    _reset_engine(monkeypatch, tmp_path)

    # Populate memory directly
    engine = api_module.get_engine()
    engine.memory.save_session(
        "Build a REST API",
        {
            "success": True,
            "files": {"api.py": "# code"},
            "review": {"score": 88, "issues": [], "suggestions": [], "approved": True},
            "tests": "def test_api(): pass",
        },
    )

    resp = client.get("/api/v1/memory")
    assert resp.status_code == 200
    sessions = resp.json()["sessions"]
    assert len(sessions) == 1
    assert sessions[0]["requirement"] == "Build a REST API"

    # Search should find it
    resp2 = client.get("/api/v1/memory/search?q=REST")
    assert resp2.status_code == 200
    assert len(resp2.json()["results"]) == 1

    # Clear and verify
    client.delete("/api/v1/memory")
    resp3 = client.get("/api/v1/memory")
    assert resp3.json()["sessions"] == []


# ---------------------------------------------------------------------------
# Queue
# ---------------------------------------------------------------------------


def test_get_queue_empty(tmp_path, monkeypatch):
    _reset_engine(monkeypatch, tmp_path)
    resp = client.get("/api/v1/queue")
    assert resp.status_code == 200
    assert resp.json()["tasks"] == []


def test_add_to_queue(tmp_path, monkeypatch):
    _reset_engine(monkeypatch, tmp_path)
    resp = client.post("/api/v1/queue", json={"requirement": "Build a hello world app"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "queued"
    assert data["task"]["requirement"] == "Build a hello world app"
    assert data["task"]["status"] == "pending"
    assert data["task"]["priority"] == 0


def test_add_to_queue_with_priority(tmp_path, monkeypatch):
    _reset_engine(monkeypatch, tmp_path)
    resp = client.post(
        "/api/v1/queue", json={"requirement": "High-priority task", "priority": 10}
    )
    assert resp.status_code == 200
    assert resp.json()["task"]["priority"] == 10


def test_queue_round_trip(tmp_path, monkeypatch):
    """Add two tasks and verify both appear in GET /api/v1/queue."""
    _reset_engine(monkeypatch, tmp_path)

    client.post("/api/v1/queue", json={"requirement": "Task A"})
    client.post("/api/v1/queue", json={"requirement": "Task B"})

    resp = client.get("/api/v1/queue")
    tasks = resp.json()["tasks"]
    assert len(tasks) == 2
    requirements = [t["requirement"] for t in tasks]
    assert "Task A" in requirements
    assert "Task B" in requirements


def test_process_queue_returns_processing(tmp_path, monkeypatch):
    """POST /api/v1/queue/process should return immediately with 'processing'."""
    _reset_engine(monkeypatch, tmp_path)
    resp = client.post("/api/v1/queue/process")
    assert resp.status_code == 200
    assert resp.json()["status"] == "processing"
