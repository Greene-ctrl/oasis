from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from oasis.social_agent.browser_manager import browser_manager

app = FastAPI(title="OASIS Browser API")


class NavigateRequest(BaseModel):
    url: str


class InteractRequest(BaseModel):
    action: str
    selector: str
    value: Optional[str] = None


@app.post("/api/agents/{agent_id}/session/start")
async def start_session(agent_id: int):
    session = browser_manager.get_session(agent_id)
    return await session.start()


@app.post("/api/agents/{agent_id}/browser/navigate")
async def navigate(agent_id: int, req: NavigateRequest):
    session = browser_manager.get_session(agent_id)
    try:
        return await session.navigate(req.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/agents/{agent_id}/browser/interact")
async def interact(agent_id: int, req: InteractRequest):
    session = browser_manager.get_session(agent_id)
    try:
        return await session.interact(req.action, req.selector, req.value)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/agents/{agent_id}/browser/dom")
async def extract_dom(agent_id: int):
    session = browser_manager.get_session(agent_id)
    try:
        return await session.extract_dom()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/agents/{agent_id}/session/close")
async def close_session(agent_id: int):
    return await browser_manager.remove_session(agent_id)


class FetchRSSRequest(BaseModel):
    url: str

@app.post("/api/agents/{agent_id}/browser/rss")
async def fetch_rss(agent_id: int, req: FetchRSSRequest):
    session = browser_manager.get_session(agent_id)
    try:
        return await session.fetch_rss_feed(req.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
