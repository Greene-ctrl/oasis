from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
import uuid

from browserbase_mcp.settings import Settings, get_settings

router = APIRouter(prefix="/api/v1/personas", tags=["personas"])

class GeneratePersonasRequest(BaseModel):
    topic: str
    count_requested: int

class PersonaProfile(BaseModel):
    id: str
    profile: str

class GeneratePersonasResponse(BaseModel):
    personas: List[PersonaProfile]
    count_actual: int

@router.post("/generate", response_model=GeneratePersonasResponse)
async def generate_personas(request: GeneratePersonasRequest, settings: Settings = Depends(get_settings)):
    # Restrict maximum based on testing mode logic
    actual_count = min(request.count_requested, settings.max_personas)

    # Generate dummy personas
    personas = []
    for i in range(actual_count):
        personas.append(PersonaProfile(
            id=str(uuid.uuid4()),
            profile=f"Persona {i+1} interested in {request.topic}"
        ))

    return GeneratePersonasResponse(
        personas=personas,
        count_actual=actual_count
    )
