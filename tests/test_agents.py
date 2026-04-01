"""
Tests for CactusRalph-Coder agents.
All tests run without a real LLM key — they test initialisation and
methods that don't require network calls.
"""

import sys
import os

import pytest

# Ensure the package root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cactus.agents import (
    BaseAgent,
    CoderAgent,
    PlannerAgent,
    ReviewerAgent,
    TesterAgent,
)
from cactus.sandbox import Sandbox


# ---------------------------------------------------------------------------
# Initialisation tests
# ---------------------------------------------------------------------------


def test_planner_agent_init():
    agent = PlannerAgent()
    assert agent.name == "PlannerAgent"


def test_coder_agent_init():
    agent = CoderAgent()
    assert agent.name == "CoderAgent"


def test_reviewer_agent_init():
    agent = ReviewerAgent()
    assert agent.name == "ReviewerAgent"


def test_tester_agent_init():
    agent = TesterAgent()
    assert agent.name == "TesterAgent"


# ---------------------------------------------------------------------------
# TesterAgent.validate_syntax — no LLM needed
# ---------------------------------------------------------------------------


def test_tester_agent_validate_syntax_valid():
    agent = TesterAgent()
    valid_code = "def add(a, b):\n    return a + b\n"
    is_valid, msg = agent.validate_syntax(valid_code)
    assert is_valid is True
    assert "valid" in msg.lower()


def test_tester_agent_validate_syntax_invalid():
    agent = TesterAgent()
    bad_code = "def broken(\n    # missing closing paren"
    is_valid, msg = agent.validate_syntax(bad_code)
    assert is_valid is False
    assert "SyntaxError" in msg or "syntax" in msg.lower()


# ---------------------------------------------------------------------------
# Sandbox.validate_syntax — no LLM needed
# ---------------------------------------------------------------------------


def test_sandbox_validate_syntax():
    sandbox = Sandbox(project_root=".")
    is_valid, msg = sandbox.validate_syntax("x = 1 + 2\nprint(x)\n")
    assert is_valid is True

    is_valid2, msg2 = sandbox.validate_syntax("x = (1 +")
    assert is_valid2 is False
    assert msg2  # should contain error info
