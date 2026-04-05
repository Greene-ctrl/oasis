from fastapi import FastAPI
from browserbase_mcp.settings import get_settings

from browserbase_mcp.routers import personas, simulation, settings

app = FastAPI(title="Browserbase MCP Personas", description="API to manage simulated personas using Browserbase MCP.")

app.include_router(personas.router)
app.include_router(simulation.router)
app.include_router(settings.router)

@app.get("/")
def read_root():
    settings_obj = get_settings()
    return {"message": "Welcome to Browserbase MCP Personas", "testing_mode": settings_obj.testing_mode, "max_personas": settings_obj.max_personas}
