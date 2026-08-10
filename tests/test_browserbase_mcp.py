import pytest
from fastapi.testclient import TestClient
from browserbase_mcp.main import app
from browserbase_mcp.settings import get_settings, Settings
import asyncio
from unittest.mock import patch, MagicMock

client = TestClient(app)

def get_settings_override():
    return Settings(testing_mode=True, browserbase_api_key="test_key")

app.dependency_overrides[get_settings] = get_settings_override

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to Browserbase MCP Personas"
    assert response.json()["testing_mode"] == True
    assert response.json()["max_personas"] == 2

def test_settings_logic():
    # Test property logic directly
    settings_testing = Settings(testing_mode=True)
    assert settings_testing.max_personas == 2

    settings_prod = Settings(testing_mode=False)
    assert settings_prod.max_personas == 22

def test_generate_personas_respects_limits():
    # In testing mode (override), should max out at 2
    response = client.post(
        "/api/v1/personas/generate",
        json={"topic": "technology", "count_requested": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count_actual"] == 2
    assert len(data["personas"]) == 2

def test_generate_personas_under_limit():
    response = client.post(
        "/api/v1/personas/generate",
        json={"topic": "technology", "count_requested": 1}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count_actual"] == 1
    assert len(data["personas"]) == 1

@patch("browserbase_mcp.mcp_client.BrowserbaseMCPClient._call_tool")
def test_simulation_start_and_status(mock_call_tool):
    # Mocking the async tool calls so background task runs without real HTTP requests
    async def async_mock(*args, **kwargs):
        return {"status": "success"}
    mock_call_tool.side_effect = async_mock

    # Start simulation requesting 5 personas (should cap at 2)
    response = client.post(
        "/api/v1/simulation/start",
        json={"target_url": "https://example.com", "task_description": "test task", "num_personas": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert data["active_personas"] == 2
    sim_id = data["simulation_id"]

    # Wait briefly for background task to execute mock calls
    # Note: TestClient does not await background tasks gracefully, so we might only see "in_progress"

    status_response = client.get(f"/api/v1/simulation/{sim_id}/status")
    assert status_response.status_code == 200
    assert "status" in status_response.json()
    assert status_response.json()["active_personas"] == 2

@pytest.mark.asyncio
async def test_mcp_client_mock():
    from browserbase_mcp.mcp_client import BrowserbaseMCPClient
    from httpx import Response

    client = BrowserbaseMCPClient(api_key="fake")

    with patch("httpx.AsyncClient.post") as mock_post:
        # Mock httpx response
        mock_response = MagicMock(spec=Response)
        mock_response.headers = {"mcp-session-id": "mock-session-id"}
        mock_response.text = 'event: message\ndata: {"result": "success"}\n\n'
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        res = await client.navigate("https://test.com")
        assert res == {"result": "success"}

        # Verify the payload structure
        args, kwargs = mock_post.call_args
        payload = kwargs["json"]
        assert payload["method"] == "tools/call"
        assert payload["params"]["name"] == "navigate"
        assert payload["params"]["arguments"] == {"url": "https://test.com"}
