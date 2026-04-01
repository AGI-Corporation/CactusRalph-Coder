"""
Memory: persistent session storage for CactusRalph-Coder.
"""

import json
import os
from datetime import datetime, timezone


class Memory:
    """Saves and retrieves coding sessions from a JSON file."""

    def __init__(self, memory_file: str):
        self.memory_file = memory_file
        os.makedirs(os.path.dirname(os.path.abspath(memory_file)), exist_ok=True)
        self._data = self._load()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load(self) -> dict:
        if not os.path.exists(self.memory_file):
            return {"sessions": []}
        try:
            with open(self.memory_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {"sessions": []}

    def _flush(self):
        with open(self.memory_file, "w") as f:
            json.dump(self._data, f, indent=2, default=str)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_session(self, requirement: str, result: dict):
        """Append a coding session to memory and persist to disk."""
        session = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "requirement": requirement,
            "success": result.get("success", False),
            "files": list(result.get("files", {}).keys()),
            "review_score": result.get("review", {}).get("score", 0),
            "issues": result.get("review", {}).get("issues", []),
        }
        self._data.setdefault("sessions", []).append(session)
        self._flush()

    def get_recent(self, n: int = 10) -> list:
        """Return the n most recent sessions."""
        sessions = self._data.get("sessions", [])
        return sessions[-n:] if len(sessions) >= n else sessions[:]

    def search(self, query: str) -> list:
        """Simple case-insensitive keyword search across session requirements."""
        query_lower = query.lower()
        return [
            s for s in self._data.get("sessions", [])
            if query_lower in s.get("requirement", "").lower()
        ]

    def clear(self):
        """Wipe all stored sessions."""
        self._data = {"sessions": []}
        self._flush()
