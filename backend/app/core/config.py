import json
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# Resolve backend/.env relative to this file so the settings load
# correctly no matter which directory the process starts from
# (backend/, the repo root, or a test runner).
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str

    DATABASE_URL: str
    SQL_ECHO: bool = False

    # Set to false when connecting through a transaction-mode pooler
    # (for example Supabase's shared pooler on port 6543), which does
    # not support prepared statements.
    DATABASE_PREPARE_STATEMENTS: bool = True

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Accepts a JSON array or a comma-separated list so hosting
    # dashboards can set it easily, e.g. on Render:
    #   BACKEND_CORS_ORIGINS=https://kyhc.vercel.app,http://localhost:5173
    BACKEND_CORS_ORIGINS: Annotated[list[str], NoDecode] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()

            if value.startswith("["):
                return json.loads(value)

            return [
                origin.strip()
                for origin in value.split(",")
                if origin.strip()
            ]

        return value

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        case_sensitive=True,
    )


settings = Settings()
