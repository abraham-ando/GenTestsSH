import os
from pathlib import Path
from dotenv import load_dotenv

# Load env from parent directory (or specific path)
env_path = Path(__file__).parent.parent / "gen-tests-self-healing" / ".env"
load_dotenv(env_path)

class Config:
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    OPENAI_RESPONSES_MODEL_ID = os.getenv("OPENAI_RESPONSES_MODEL_ID") or OPENAI_MODEL
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # For local LLMs
    
    # Paths
    BACKEND_DIR = Path(__file__).parent
    
config = Config()
