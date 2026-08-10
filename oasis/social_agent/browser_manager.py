import asyncio
from typing import Any, Dict, Optional
import httpx
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import urlparse, urljoin

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

    async def _is_blocked(self) -> bool:
        """Check if the current page is blocked by Cloudflare/CAPTCHA."""
        content = await self.page.content()
        if "cloudflare" in content.lower() or "challenge" in content.lower() or "just a moment" in content.lower():
            # Cloudflare often uses specific titles or phrases
            if "<title>Just a moment...</title>" in content or "Please wait while your request is being verified" in content:
                return True
        return False

    async def _discover_rss(self, base_url: str) -> Optional[str]:
        """Attempt to auto-discover RSS feed URL via common paths or HTML tags."""
        parsed = urlparse(base_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        # 1. Try to fetch the homepage and look for link rel="alternate"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
                resp = await client.get(domain, headers=headers)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    link_tags = soup.find_all('link', type='application/rss+xml')
                    if link_tags and link_tags[0].has_attr('href'):
                        return urljoin(domain, link_tags[0]['href'])
        except Exception:
            pass

        # 2. Try common paths
        common_paths = ['/feed', '/rss', '/feed.xml', '/rss.xml', '/news/rss']
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
                for path in common_paths:
                    test_url = urljoin(domain, path)
                    resp = await client.get(test_url, headers=headers)
                    if resp.status_code == 200 and ('xml' in resp.headers.get('Content-Type', '').lower() or 'rss' in resp.text.lower()[:200]):
                        return test_url
        except Exception:
            pass

        return None

    async def navigate(self, url: str):
        if not self.started:
            raise Exception("Browser not started")

        await self.page.goto(url, wait_until="domcontentloaded")

        # Approach 1: RSS Auto-Discovery if blocked
        if await self._is_blocked():
            rss_url = await self._discover_rss(url)
            if rss_url:
                # Approach 4: Hybrid read mode
                # Since we were trying to navigate to a specific article (url)
                # but got blocked, let's fetch the RSS feed and see if we can find
                # the article summary in the feed to return as the "content".
                feed_data = await self.fetch_rss_feed(rss_url)

                if feed_data.get("status") == "success":
                    for article in feed_data.get("articles", []):
                        if article.get("link") == url or url in article.get("link", ""):
                            # We found the blocked article in the RSS feed!
                            hybrid_dom = f"<html><body><h1>{article.get('title')}</h1><p>{article.get('summary')}</p></body></html>"
                            # We can't easily inject this into playwright without weird side effects,
                            # so we just return the summary directly as a warning text, or we can use
                            # page.set_content(hybrid_dom) to render it!
                            await self.page.set_content(hybrid_dom)
                            return {
                                "status": "success",
                                "url": url,
                                "warning": "Blocked by Cloudflare/CAPTCHA. Hybrid mode: displaying RSS summary instead of full article."
                            }

                # If hybrid mode failed (article not in recent feed items), fallback to the RSS feed page
                await self.page.goto(rss_url, wait_until="domcontentloaded")
                return {"status": "success", "url": rss_url, "warning": "Blocked by Cloudflare/CAPTCHA. Auto-redirected to RSS feed."}
            else:
                return {"status": "success", "url": url, "warning": "Blocked by Cloudflare/CAPTCHA. No RSS feed auto-discovered."}

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

    async def fetch_rss_feed(self, url: str) -> Dict[str, Any]:
        """Explicitly fetch and parse an RSS feed."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    feed = feedparser.parse(resp.text)
                    articles = []
                    for entry in feed.entries[:10]: # Limit to top 10
                        articles.append({
                            "title": entry.get("title", ""),
                            "link": entry.get("link", ""),
                            "summary": entry.get("summary", "")[:500] # Limit summary length
                        })
                    return {
                        "status": "success",
                        "feed_title": feed.feed.get("title", ""),
                        "articles": articles
                    }
                else:
                    return {"status": "error", "message": f"Failed to fetch RSS, status code: {resp.status_code}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


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
