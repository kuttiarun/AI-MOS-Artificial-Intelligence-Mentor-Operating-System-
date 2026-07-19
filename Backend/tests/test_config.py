"""
AI-MOS Backend — Config Service Unit Tests
============================================
Tests settings parsing logic, environment variable defaults, and CORS origin splitting.
"""

import os
from unittest.mock import patch
from app.core.config import Settings


def test_cors_origins_parsing_from_string():
    """
    Verifies that a comma-separated string of CORS origins is correctly parsed
    into a type-safe List[str] by the field validator.
    """
    # Test case 1: Comma-separated list with spaces
    config = Settings(
        SECRET_KEY="test_secret",
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        CORS_ORIGINS="http://localhost:3000, https://aimos.dev , http://localhost:5173",
    )
    assert config.CORS_ORIGINS == [
        "http://localhost:3000",
        "https://aimos.dev",
        "http://localhost:5173",
    ]

    # Test case 2: Single origin string
    config_single = Settings(
        SECRET_KEY="test_secret",
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        CORS_ORIGINS="http://localhost:3000",
    )
    assert config_single.CORS_ORIGINS == ["http://localhost:3000"]

    # Test case 3: Already a list
    config_list = Settings(
        SECRET_KEY="test_secret",
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        CORS_ORIGINS=["http://localhost:3000", "https://aimos.dev"],
    )
    assert config_list.CORS_ORIGINS == ["http://localhost:3000", "https://aimos.dev"]
