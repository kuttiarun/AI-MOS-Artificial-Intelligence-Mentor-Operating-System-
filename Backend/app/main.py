"""
AI-MOS Backend — Application Entry Point
=========================================
Instantiates the FastAPI application, wires up all middleware,
attaches the v1 API router, and exposes the liveness probe endpoint.

Run locally:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Production:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.schemas.gateway import HealthResponse

# Configure structured logging
logging.basicConfig(
    level=logging.DEBUG if not settings.is_production else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# =============================================================================
# FastAPI Application Instance
# =============================================================================
@asynccontextmanager
async def lifespan(application: FastAPI):
    """
    FastAPI lifespan context manager — replaces deprecated on_event handlers.
    Code before `yield` runs on startup; code after `yield` runs on shutdown.
    """
    logger.info(
        "AI-MOS Gateway starting up | environment=%s | cors_origins=%s",
        settings.ENVIRONMENT,
        settings.CORS_ORIGINS,
    )
    yield
    logger.info("AI-MOS Gateway shutting down gracefully.")


app = FastAPI(
    title="AI-MOS Gateway",
    description=(
        "**AI-MOS** (Artificial Intelligence Mentor Operating System) — "
        "Stateless BYOK Orchestration and Context Injection Framework.\n\n"
        "This API serves as the pedagogical gateway between the student's "
        "browser and their chosen LLM compute provider, enforcing first-principles "
        "learning constraints on every interaction."
    ),
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
    openapi_url="/openapi.json",
    contact={
        "name": "AI-MOS Engineering",
    },
    license_info={
        "name": "Proprietary",
    },
    lifespan=lifespan,
)

# =============================================================================
# CORS Middleware
# =============================================================================
# Origins are loaded from CORS_ORIGINS environment variable (pydantic-settings).
# Default: ["http://localhost:5173"] — Vite dev server.
# Production: Set CORS_ORIGINS to your actual domain(s) in .env.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-User-API-Key",    # BYOK header (SRS §3)
        "X-User-Provider",   # Provider selector header (SRS §3)
        "X-User-Id",         # Student User ID header
        "Accept",
        "Origin",
    ],
    expose_headers=[
        "Content-Type",
        "Cache-Control",
        "X-Accel-Buffering",
    ],
)

# =============================================================================
# Router Registration
# =============================================================================
# All v1 routes are mounted under /api/v1.
# The api_router in app/api/v1/api.py aggregates all sub-routers.
app.include_router(api_router, prefix="/api/v1")

# =============================================================================
# Health Probe
# =============================================================================
@app.get(
    "/health",
    summary="Liveness Probe",
    description="Simple liveness check confirming the FastAPI process is running.",
    response_model=HealthResponse,
    tags=["System"],
)
async def health_check() -> HealthResponse:
    """
    Used by Docker health checks, Kubernetes liveness probes, and
    monitoring systems to verify the service is alive.
    """
    return HealthResponse(
        status="healthy",
        engine="AI-MOS FastAPI Gateway",
        environment=settings.ENVIRONMENT,
    )
