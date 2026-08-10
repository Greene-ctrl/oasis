import httpx
from typing import Dict, Any, Optional

class BrowserbaseMCPClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://mcp.browserbase.com/mcp"
        self.client = httpx.AsyncClient(timeout=60.0)
        self.session_id: Optional[str] = None
        self._request_id = 1

    async def initialize(self) -> None:
        """Initializes the MCP session with Browserbase and retrieves the mcp-session-id."""
        url = f"{self.base_url}?browserbaseApiKey={self.api_key}"
        payload = {
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "oasis-mcp", "version": "1.0"}
            },
            "jsonrpc": "2.0",
            "id": self._request_id
        }
        self._request_id += 1

        headers = {
            "Accept": "application/json, text/event-stream"
        }

        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()

        # Extract mcp-session-id from headers
        self.session_id = response.headers.get("mcp-session-id")
        if not self.session_id:
            raise Exception("Failed to retrieve mcp-session-id from Browserbase MCP server initialization")

    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to call an MCP tool."""
        if not self.session_id:
            await self.initialize()

        url = f"{self.base_url}?browserbaseApiKey={self.api_key}"
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": self._request_id
        }
        self._request_id += 1

        headers = {
            "mcp-session-id": self.session_id,
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }

        try:
            response = await self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            # The server responds with SSE format (event: message\ndata: {json}\n\n)
            text = response.text
            data_line = next((line for line in text.split("\n") if line.startswith("data: ")), None)

            if data_line:
                import json
                return json.loads(data_line[6:])
            else:
                return {"error": "Invalid SSE response format", "content": text}
        except httpx.HTTPError as e:
            return {"error": str(e), "content": getattr(e, "response", None) and e.response.text}

    async def start(self) -> Dict[str, Any]:
        """Starts the Browserbase session for this context."""
        return await self._call_tool("start", {})

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
