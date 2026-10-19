import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

class Config:
    # LLM Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    
    # FalkorDB Database Settings
    FALKORDB_HOST: str = os.getenv("FALKORDB_HOST", "localhost")
    FALKORDB_PORT: int = int(os.getenv("FALKORDB_PORT", "6379"))
    FALKORDB_USERNAME: str | None = os.getenv("FALKORDB_USERNAME", None) or None
    FALKORDB_PASSWORD: str | None = os.getenv("FALKORDB_PASSWORD", None) or None
    FALKORDB_GRAPH_NAME: str = os.getenv("FALKORDB_GRAPH_NAME", "scamtrace")
    
    # Backend Server Settings
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Agent Guardrails
    MAX_TRAVERSAL_DEPTH: int = 4
    MAX_QUERY_NODES: int = 50

config = Config()
