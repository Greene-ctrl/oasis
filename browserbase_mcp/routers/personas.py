from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
import uuid
import json
import os

from browserbase_mcp.settings import Settings, get_settings

# We will import the OASIS generation logic, assuming the user has Reddit data in the data folder.
from oasis.social_agent.agents_generator import generate_reddit_agent_graph

router = APIRouter(prefix="/api/v1/personas", tags=["personas"])

class GeneratePersonasRequest(BaseModel):
    topic: str
    count_requested: int

class PersonaProfile(BaseModel):
    id: str
    name: str
    profile: str

class GeneratePersonasResponse(BaseModel):
    personas: List[PersonaProfile]
    count_actual: int

@router.post("/generate", response_model=GeneratePersonasResponse)
async def generate_personas(request: GeneratePersonasRequest, settings: Settings = Depends(get_settings)):
    # Restrict maximum based on testing mode logic
    actual_count = min(request.count_requested, settings.max_personas)

    personas = []

    # Try to load real personas using OASIS logic
    profile_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "reddit", "user_data_36.json")
    if os.path.exists(profile_path):
        try:
            # generate_reddit_agent_graph creates real agent profiles based on the json file
            # it takes a profile path and creates the graph.
            agent_graph = await generate_reddit_agent_graph(profile_path=profile_path)

            agents = agent_graph.get_agents()
            for agent_id, agent in list(agents)[:actual_count]:
                personas.append(PersonaProfile(
                    id=str(agent_id),
                    name=agent.user_info.name,
                    profile=agent.user_info.profile.get("other_info", {}).get("user_profile", f"Interested in {request.topic}")
                ))
        except Exception as e:
            print("Error loading OASIS personas:", str(e))

    # Fallback if file doesn't exist or not enough agents
    while len(personas) < actual_count:
        personas.append(PersonaProfile(
            id=str(uuid.uuid4()),
            name=f"Fallback User {len(personas)+1}",
            profile=f"Persona {len(personas)+1} interested in {request.topic}"
        ))

    return GeneratePersonasResponse(
        personas=personas,
        count_actual=actual_count
    )
