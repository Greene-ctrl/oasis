import asyncio
from typing import Any, Dict, Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright


class BrowserSession:
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        self.playwright: Any = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.started = False

    async def start(self):
        if self.started:
            return {"status": "started", "agent_id": self.agent_id}

        self.playwright = await async_playwright().start()
        # Use headless true for testing environment,
        # could be configured via env
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.started = True
        return {"status": "started", "agent_id": self.agent_id}

    async def navigate(self, url: str):
        if not self.started:
            raise Exception("Browser not started")
        await self.page.goto(url, wait_until="domcontentloaded")
        return {"status": "success", "url": url}

    async def interact(
        self, action: str, selector: str, value: Optional[str] = None
    ):
        if not self.started:
            raise Exception("Browser not started")

        if action == "click":
            await self.page.click(selector)
        elif action == "type_text":
            if value is None:
                raise Exception("Value is required for type_text action")
            await self.page.fill(selector, value)
        else:
            raise Exception(f"Unsupported action: {action}")

        interaction = {"action": action, "selector": selector, "value": value}
        return {"status": "success", "interaction": interaction}

    async def extract_dom(self):
        if not self.started:
            raise Exception("Browser not started")
        content = await self.page.content()
        return {"status": "success", "dom": content}

    async def close(self):
        if self.started:
            await self.page.close()
            await self.context.close()
            await self.browser.close()
            await self.playwright.stop()
            self.started = False
        return {"status": "success"}


class BrowserManager:
    def __init__(self):
        self.sessions: Dict[int, BrowserSession] = {}

    def get_session(self, agent_id: int) -> BrowserSession:
        if agent_id not in self.sessions:
            self.sessions[agent_id] = BrowserSession(agent_id)
        return self.sessions[agent_id]

    async def remove_session(self, agent_id: int):
        if agent_id in self.sessions:
            await self.sessions[agent_id].close()
            del self.sessions[agent_id]
        return {"status": "success"}


browser_manager = BrowserManager()
