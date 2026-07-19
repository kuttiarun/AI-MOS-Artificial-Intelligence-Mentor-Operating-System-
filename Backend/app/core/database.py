"""
AI-MOS Backend — Async Database Engine & Session Factory
=========================================================
Provides the SQLAlchemy async engine, session factory, and the
FastAPI dependency injector `get_db()` used by all route handlers
that need database access.

Architecture note:
- We use async SQLAlchemy (asyncpg driver) to avoid blocking the
  FastAPI event loop during database queries.
- The `Base` declarative base is defined here so ORM models can
  import it without circular dependency issues.

Usage in a route handler:
    from app.core.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    @router.get("/example")
    async def example(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(User))
        ...
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# =============================================================================
# Async Engine
# =============================================================================
# echo=False in production to avoid leaking SQL statements to logs.
# pool_pre_ping=True validates connections before use — critical for
# long-lived processes where the DB connection may have timed out.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=not settings.is_production,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# =============================================================================
# Session Factory
# =============================================================================
# expire_on_commit=False prevents attributes from expiring after commit,
# which would cause lazy-load errors in async contexts.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# =============================================================================
# ORM Declarative Base
# =============================================================================
# All ORM model classes inherit from this Base.
# Alembic's env.py imports `Base.metadata` to autogenerate migrations.
class Base(DeclarativeBase):
    """Shared declarative base for all AI-MOS ORM models."""
    pass


# =============================================================================
# FastAPI Dependency: get_db
# =============================================================================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator that yields a database session per request.
    The session is automatically closed after the request completes,
    even if an exception is raised.

    Inject with: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
