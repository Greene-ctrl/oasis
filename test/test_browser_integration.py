import asyncio

import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from oasis.social_agent.browser_app import app
from oasis.social_agent.browser_manager import browser_manager


@pytest.fixture(autouse=True)
async def clear_sessions():
    for session in list(browser_manager.sessions.values()):
        await session.close()
    browser_manager.sessions.clear()
    yield
    for session in list(browser_manager.sessions.values()):
        await session.close()
    browser_manager.sessions.clear()


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_session_start():
    agent_id = 1
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(f"/api/agents/{agent_id}/session/start")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        assert data["agent_id"] == agent_id
        assert agent_id in browser_manager.sessions
        assert browser_manager.sessions[agent_id].started is True


@pytest.mark.anyio
async def test_navigate_without_start_fails():
    agent_id = 2
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            f"/api/agents/{agent_id}/browser/navigate",
            json={"url": "https://example.com"},
        )
        assert response.status_code == 400
        assert "Browser not started" in response.json()["detail"]


@pytest.mark.anyio
async def test_navigate_success():
    agent_id = 3
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await ac.post(f"/api/agents/{agent_id}/session/start")

        response = await ac.post(
            f"/api/agents/{agent_id}/browser/navigate",
            json={"url": "https://example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["url"] == "https://example.com"

        # test extract dom
        dom_response = await ac.get(f"/api/agents/{agent_id}/browser/dom")
        assert dom_response.status_code == 200
        assert "Example Domain" in dom_response.json()["dom"]


@pytest.mark.anyio
async def test_interact():
    agent_id = 4
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await ac.post(f"/api/agents/{agent_id}/session/start")
        await ac.post(
            f"/api/agents/{agent_id}/browser/navigate",
            json={"url": "https://example.com"},
        )

        # example.com has an h1 and p tags
        response = await ac.post(
            f"/api/agents/{agent_id}/browser/interact",
            json={"action": "click", "selector": "h1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


@pytest.mark.anyio
async def test_session_close():
    agent_id = 5
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await ac.post(f"/api/agents/{agent_id}/session/start")

        assert agent_id in browser_manager.sessions

        response = await ac.post(f"/api/agents/{agent_id}/session/close")
        assert response.status_code == 200
        assert agent_id not in browser_manager.sessions
