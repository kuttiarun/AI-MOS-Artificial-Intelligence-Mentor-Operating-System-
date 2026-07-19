"""
AI-MOS Backend — Core Settings Configuration
=============================================
Uses pydantic-settings to validate and expose all environment variables
as a type-safe singleton. Any missing required variable raises a clear
startup error instead of a silent runtime fault.

Usage:
    from app.core.config import settings
    print(settings.DATABASE_URL)
"""

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Validated environment configuration loaded from the .env file
    at application startup. All fields are strictly typed.
    """

    model_config = SettingsConfigDict(
        # Look for the .env file one directory above app/ (i.e., backend/.env)
        env_file=".env",
        env_file_encoding="utf-8",
        # Allow extra fields to pass through without raising validation errors
        # (useful for Docker Compose env vars like POSTGRES_DB)
        extra="ignore",
        case_sensitive=False,
    )

    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------
    ENVIRONMENT: str = "development"

    # -------------------------------------------------------------------------
    # Security — JWT
    # -------------------------------------------------------------------------
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # -------------------------------------------------------------------------
    # Database — PostgreSQL (async DSN)
    # Format: postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DBNAME
    # -------------------------------------------------------------------------
    DATABASE_URL: str

    # -------------------------------------------------------------------------
    # CORS
    # Stored as a comma-separated string in .env, parsed to a list here.
    # Example: CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
    # -------------------------------------------------------------------------
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Allows passing a comma-separated string of origins (e.g. from .env or Docker Env)"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # -------------------------------------------------------------------------
    # Derived helpers
    # -------------------------------------------------------------------------
    @property
    def is_production(self) -> bool:
        """True when running in the production deployment environment."""
        return self.ENVIRONMENT.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Returns a cached Settings singleton.
    The lru_cache ensures the .env file is read exactly once per process
    lifetime, preventing redundant I/O on every import.
    """
    return Settings()


# Module-level singleton — import this everywhere
settings: Settings = get_settings()
