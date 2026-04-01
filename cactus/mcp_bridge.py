"""
MCPBridge: integrates CactusRalph-Coder with Route.X via the Model Context Protocol.
"""

import base64
import os

import requests


class MCPBridge:
    """Sends tool calls to a Route.X MCP server."""

    def __init__(self, mcp_url: str = None, api_key: str = None):
        self.mcp_url = mcp_url or os.environ.get("ROUTEX_MCP_URL", "")
        self.api_key = api_key or os.environ.get("ROUTEX_API_KEY", "")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers["Authorization"] = f"Bearer {self.api_key}"
        self.session.headers["Content-Type"] = "application/json"

    # ------------------------------------------------------------------
    # Core MCP helpers
    # ------------------------------------------------------------------

    def call_tool(self, tool_name: str, params: dict) -> dict:
        """
        Invoke a named tool on the MCP server.

        Returns the parsed JSON response body.
        """
        if not self.mcp_url:
            raise RuntimeError("ROUTEX_MCP_URL is not configured.")

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params,
            },
        }
        response = self.session.post(self.mcp_url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def list_tools(self) -> list:
        """Return a list of tools available on the MCP server."""
        if not self.mcp_url:
            raise RuntimeError("ROUTEX_MCP_URL is not configured.")

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }
        response = self.session.post(self.mcp_url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("result", {}).get("tools", [])

    # ------------------------------------------------------------------
    # GitHub MCP convenience method
    # ------------------------------------------------------------------

    def github_create_file(
        self,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str = "main",
    ) -> dict:
        """
        Create or update a file in a GitHub repo via the GitHub MCP tool.

        Args:
            repo:    repository in "owner/name" format
            path:    file path within the repo
            content: raw file content (will be base64-encoded)
            message: commit message
            branch:  target branch (default: "main")
        """
        encoded = base64.b64encode(content.encode()).decode()
        return self.call_tool(
            "github_create_or_update_file",
            {
                "repo": repo,
                "path": path,
                "content": encoded,
                "message": message,
                "branch": branch,
            },
        )
