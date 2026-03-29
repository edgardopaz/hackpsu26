import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


_env_path = Path(__file__).resolve().parents[2] / ".env"
if _env_path.is_file():
    load_dotenv(_env_path)


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    tavily_api_key: str
    frontend_origin: str
    frontend_origins: str

    @property
    def allowed_origins(self) -> list[str]:
        origins = {
            self.frontend_origin,
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        }
        extra_origins = {
            origin.strip()
            for origin in self.frontend_origins.split(",")
            if origin.strip()
        }
        origins.update(extra_origins)
        return sorted(o.rstrip("/") for o in origins if o)


@lru_cache
def get_settings() -> Settings:
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        frontend_origin=os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
        frontend_origins=os.getenv("FRONTEND_ORIGINS", ""),
    )
