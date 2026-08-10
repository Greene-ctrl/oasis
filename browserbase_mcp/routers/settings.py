from fastapi import APIRouter, Depends
from pydantic import BaseModel

from browserbase_mcp.settings import Settings, get_settings

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])

class UpdateSettingsRequest(BaseModel):
    testing_mode: bool
    browserbase_api_key: str = None

class SettingsResponse(BaseModel):
    testing_mode: bool
    max_personas: int
    browserbase_api_key_configured: bool

@router.get("", response_model=SettingsResponse)
async def get_current_settings(settings: Settings = Depends(get_settings)):
    return SettingsResponse(
        testing_mode=settings.testing_mode,
        max_personas=settings.max_personas,
        browserbase_api_key_configured=bool(settings.browserbase_api_key)
    )

@router.put("", response_model=SettingsResponse)
async def update_settings(request: UpdateSettingsRequest, settings: Settings = Depends(get_settings)):
    settings.testing_mode = request.testing_mode
    if request.browserbase_api_key is not None:
        settings.browserbase_api_key = request.browserbase_api_key

    return SettingsResponse(
        testing_mode=settings.testing_mode,
        max_personas=settings.max_personas,
        browserbase_api_key_configured=bool(settings.browserbase_api_key)
    )
