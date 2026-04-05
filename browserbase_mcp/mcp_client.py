import httpx
import json
from typing import Dict, Any, Optional
import asyncio

class BrowserbaseMCPClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://mcp.browserbase.com/mcp"
        self.client = httpx.AsyncClient(timeout=60.0)

    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to call an MCP tool."""
        # For simplicity, we implement this as a direct HTTP POST call if the endpoint supports it.
        # Alternatively, using the official python `mcp` library client.
        # Since standard MCP HTTP POST is typically `/tools/{tool_name}/call` or similar:
        # However, the exact HTTP format for Browserbase MCP might require Server-Sent Events (SSE) or simple JSON RPC.
        # We will use the standard structure. We will implement it directly via POST to the mcp URL if it supports simple POSTs for tool calls.
        # But generally, for MCP over SSE, you need to connect to SSE first, get the POST endpoint, then POST the tool call.
        # Let's write a generic request structure. In a real scenario, we might use `mcp` SDK if it supports HTTP transport out of the box.

        url = f"{self.base_url}?browserbaseApiKey={self.api_key}"

        # This is a mocked/simplified version of an MCP JSON-RPC call.
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 1
        }

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": str(e)}

    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigates to a specific URL."""
        return await self._call_tool("navigate", {"url": url})

    async def observe(self) -> Dict[str, Any]:
        """Observes the current page state."""
        return await self._call_tool("observe", {})

    async def act(self, action: str) -> Dict[str, Any]:
        """Performs an action on the page."""
        return await self._call_tool("act", {"action": action})

    async def close(self):
        await self.client.aclose()
