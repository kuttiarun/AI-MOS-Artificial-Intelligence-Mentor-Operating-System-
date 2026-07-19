"""
AI-MOS Backend — API v1 Router Accumulator
==========================================
Central registry that collects all v1 sub-routers and applies
consistent path prefixes and tags. This file is the ONLY place
to register new v1 endpoints — main.py imports this single router.

Adding a new module in Phase 2+:
    1. Create app/api/v1/endpoints/your_module.py
    2. Import the router here
    3. Add an api_router.include_router(...) call below
    4. Done — main.py requires no changes.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, curriculum, gateway

api_router = APIRouter()

# ---------------------------------------------------------------------------
# Gateway — BYOK AI Streaming (MOD-04)
# All routes: /api/v1/gateway/*
# ---------------------------------------------------------------------------
api_router.include_router(
    gateway.router,
    prefix="/gateway",
    tags=["AI Gateway"],
)

# ---------------------------------------------------------------------------
# Authentication — User Registration & Session Management (Day 3)
# All routes: /api/v1/auth/*
# ---------------------------------------------------------------------------
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# ---------------------------------------------------------------------------
# Curriculum — Progress Validation & Node Unlocking (Phase 4)
# All routes: /api/v1/curriculum/*
# ---------------------------------------------------------------------------
api_router.include_router(
    curriculum.router,
    prefix="/curriculum",
    tags=["Curriculum"],
)
