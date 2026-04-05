import httpx
from typing import Dict, Any, Optional
import json

class GradioMCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self._request_id = 1
        self.current_url: Optional[str] = None

    async def initialize(self) -> None:
        """Initializes the MCP session. With Gradio MCP, this just ensures basic connectivity if needed."""
        pass # Gradio MCP does not require session initialization or mcp-session-id

    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Helper to call an MCP tool."""
        if arguments is None:
            arguments = {}

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
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }

        try:
            response = await self.client.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()

            # The server responds with SSE format (event: message\ndata: {json}\n\n)
            text = response.text
            data_line = next((line for line in text.split("\n") if line.startswith("data: ")), None)

            if data_line:
                return json.loads(data_line[6:])
            else:
                return {"error": "Invalid SSE response format", "content": text}
        except httpx.HTTPError as e:
            return {"error": str(e), "content": getattr(e, "response", None) and e.response.text}

    async def start(self) -> Dict[str, Any]:
        """Starts the Browserbase session for this context."""
        # Gradio MCP doesn't have an explicit start tool, we return a success mock
        return {"result": {"content": [{"text": "Session started", "type": "text"}]}}

    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigates to a specific URL. For Gradio, we just save the url for subsequent actions."""
        self.current_url = url
        # We can map navigate to get_html_source to actually load the page
        return await self._call_tool("get_html_source", {"url": self.current_url})

    async def observe(self) -> Dict[str, Any]:
        """Observes the current page state."""
        if not self.current_url:
            return {"error": "No URL set. Call navigate first."}
        return await self._call_tool("get_page_info", {"url": self.current_url})

    async def act(self, action: str) -> Dict[str, Any]:
        """Performs an action on the page."""
        if not self.current_url:
            return {"error": "No URL set. Call navigate first."}

        action_lower = action.lower()
        if "scroll" in action_lower:
            direction = "bottom" if "down" in action_lower else "top"
            return await self._call_tool("scroll_page", {
                "url": self.current_url,
                "direction": direction,
                "pixels": 500
            })
        elif "click" in action_lower:
            # We would need a selector. For now, we mock a click on body or pass a generic execute_js if no selector is given
            # But "click" tool exists
            return await self._call_tool("click", {"url": self.current_url, "selector": "body"})
        elif "fill" in action_lower:
            return await self._call_tool("fill", {"url": self.current_url, "selector": "body", "text": "test"})

        # Fallback to js execution if it doesn't match
        return await self._call_tool("execute_js", {"url": self.current_url, "javascript_code": f"console.log('Action: {action}')"})

    async def close(self):
        await self.client.aclose()
