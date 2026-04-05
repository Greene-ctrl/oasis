from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
import asyncio
import uuid
from typing import Dict, Any

from browserbase_mcp.settings import Settings, get_settings
from browserbase_mcp.mcp_client import GradioMCPClient

router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])

class StartSimulationRequest(BaseModel):
    target_url: str
    task_description: str
    num_personas: int

class StartSimulationResponse(BaseModel):
    simulation_id: str
    status: str
    active_personas: int

# In-memory store for simulation statuses
simulations_store: Dict[str, Dict[str, Any]] = {}

async def run_persona_session(persona_id: str, target_url: str, mcp_base_url: str, simulation_id: str):
    client = GradioMCPClient(base_url=mcp_base_url)
    simulations_store[simulation_id]["logs"].append(f"[{persona_id}] Starting session...")

    try:
        # Start browser session
        simulations_store[simulation_id]["logs"].append(f"[{persona_id}] Initializing browser session...")
        await client.start()

        # Navigate
        simulations_store[simulation_id]["logs"].append(f"[{persona_id}] Navigating to {target_url}...")
        await client.navigate(target_url)

        # Simulate wait and observe
        await asyncio.sleep(2)
        simulations_store[simulation_id]["logs"].append(f"[{persona_id}] Observing page...")
        await client.observe()

        # Simulate act
        await asyncio.sleep(2)
        simulations_store[simulation_id]["logs"].append(f"[{persona_id}] Performing action...")
        await client.act("Scroll down")

        simulations_store[simulation_id]["logs"].append(f"[{persona_id}] Session completed successfully.")
    except Exception as e:
        simulations_store[simulation_id]["logs"].append(f"[{persona_id}] Error: {str(e)}")
    finally:
        await client.close()

async def run_simulation_orchestrator(simulation_id: str, target_url: str, num_personas: int, mcp_base_url: str):
    tasks = []
    for i in range(num_personas):
        persona_id = f"persona_{i+1}"
        tasks.append(run_persona_session(persona_id, target_url, mcp_base_url, simulation_id))

    await asyncio.gather(*tasks)
    simulations_store[simulation_id]["status"] = "completed"

@router.post("/start", response_model=StartSimulationResponse)
async def start_simulation(request: StartSimulationRequest, background_tasks: BackgroundTasks, settings: Settings = Depends(get_settings)):
    simulation_id = str(uuid.uuid4())

    # Restrict actual count
    actual_count = min(request.num_personas, settings.max_personas)

    simulations_store[simulation_id] = {
        "status": "in_progress",
        "active_personas": actual_count,
        "logs": []
    }

    background_tasks.add_task(
        run_simulation_orchestrator,
        simulation_id=simulation_id,
        target_url=request.target_url,
        num_personas=actual_count,
        mcp_base_url=settings.mcp_base_url
    )

    return StartSimulationResponse(
        simulation_id=simulation_id,
        status="running",
        active_personas=actual_count
    )

@router.get("/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    if simulation_id not in simulations_store:
        return {"error": "Simulation not found"}

    return simulations_store[simulation_id]
