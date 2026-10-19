"""
ScamTrace FastAPI Application Entrypoint.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config
from app.database.falkor_client import FalkorDBManager
from app.api.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize and seed FalkorDB
    db = FalkorDBManager.get_instance()
    db.seed_database(force=False)
    yield
    # Shutdown logic if needed


app = FastAPI(
    title="ScamTrace API",
    version="1.0.0",
    description="FalkorDB Graph-Powered AI Scam Investigation Platform",
    lifespan=lifespan
)

# Enable CORS for local Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    db = FalkorDBManager.get_instance()
    return {
        "name": "ScamTrace — Graph-Powered AI Scam Investigation Agent",
        "hackathon": "FalkorDB Graph Hacks (Track 01: Agents That Act on Connected Data)",
        "status": "operational",
        "falkordb_status": db.health_check()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=config.BACKEND_HOST, port=config.BACKEND_PORT, reload=True)
