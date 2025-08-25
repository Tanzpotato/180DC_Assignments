import os
from functools import lru_cache
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOTENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=DOTENV_PATH)

class Settings:
    PROVIDER: str = os.getenv("LLM_PROVIDER", "llama2")
    MODEL: str = os.getenv("LLM_MODEL", "llama2:7b")
    USE_MOCK: bool = os.getenv("USE_MOCK", "false").lower() == "true"
    TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "180"))

@lru_cache
def get_settings() -> Settings:
    return Settings()
