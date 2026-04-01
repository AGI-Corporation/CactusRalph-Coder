"""
Tests for CactusEngine and Memory.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cactus.engine import CactusEngine
from cactus.memory import Memory


# ---------------------------------------------------------------------------
# Engine initialisation
# ---------------------------------------------------------------------------


def test_engine_init(tmp_path):
    engine = CactusEngine(project_root=str(tmp_path))
    assert engine.project_root == str(tmp_path)
    assert engine.planner is not None
    assert engine.coder is not None
    assert engine.reviewer is not None
    assert engine.tester is not None
    assert engine.memory is not None
    assert engine.sandbox is not None


# ---------------------------------------------------------------------------
# Memory: save and retrieve
# ---------------------------------------------------------------------------


def test_memory_save_and_retrieve(tmp_path):
    mem_file = str(tmp_path / "test_memory.json")
    memory = Memory(mem_file)

    result = {
        "success": True,
        "files": {"main.py": "print('hello')"},
        "review": {"score": 85, "issues": [], "suggestions": [], "approved": True},
        "tests": "def test_main(): pass",
    }
    memory.save_session("Create a hello world script", result)

    recent = memory.get_recent(5)
    assert len(recent) == 1
    assert recent[0]["requirement"] == "Create a hello world script"
    assert recent[0]["success"] is True
    assert recent[0]["review_score"] == 85


def test_memory_get_recent_multiple(tmp_path):
    mem_file = str(tmp_path / "test_memory2.json")
    memory = Memory(mem_file)

    for i in range(5):
        memory.save_session(
            f"Requirement {i}",
            {"success": True, "files": {}, "review": {"score": 70, "issues": [], "suggestions": [], "approved": True}, "tests": ""},
        )

    recent = memory.get_recent(3)
    assert len(recent) == 3
    # Verify we got the three most recent requirements (indices 2, 3, 4)
    assert recent[0]["requirement"] == "Requirement 2"
    assert recent[1]["requirement"] == "Requirement 3"
    assert recent[-1]["requirement"] == "Requirement 4"


# ---------------------------------------------------------------------------
# Memory: search
# ---------------------------------------------------------------------------


def test_memory_search(tmp_path):
    mem_file = str(tmp_path / "test_memory3.json")
    memory = Memory(mem_file)

    memory.save_session(
        "Build a REST API with FastAPI",
        {"success": True, "files": {}, "review": {"score": 80, "issues": [], "suggestions": [], "approved": True}, "tests": ""},
    )
    memory.save_session(
        "Write a data pipeline in pandas",
        {"success": False, "files": {}, "review": {"score": 50, "issues": [], "suggestions": [], "approved": False}, "tests": ""},
    )

    results = memory.search("FastAPI")
    assert len(results) == 1
    assert "FastAPI" in results[0]["requirement"]

    all_results = memory.search("pipeline")
    assert len(all_results) == 1

    no_results = memory.search("kubernetes")
    assert len(no_results) == 0


def test_memory_clear(tmp_path):
    mem_file = str(tmp_path / "test_memory4.json")
    memory = Memory(mem_file)

    memory.save_session(
        "Some task",
        {"success": True, "files": {}, "review": {"score": 90, "issues": [], "suggestions": [], "approved": True}, "tests": ""},
    )
    assert len(memory.get_recent()) == 1

    memory.clear()
    assert len(memory.get_recent()) == 0
