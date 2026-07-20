"""
AI-MOS Backend — AI Gateway Endpoint
======================================
Implements POST /api/v1/gateway/chat — the core BYOK streaming route.

Data flow (Phase 2):
  1. Resolve User ID (from X-User-Id header or fallback to seeded test user)
  2. Fetch Curriculum Node from DB to locate the markdown path
  3. Load lesson text asynchronously via the cached KnowledgeBaseService
  4. Query user's progress and active weak areas from PostgreSQL
  5. Compile Socratic pedagogical prompt, including "No Code" trigger if failures >= 1
  6. Forward request to LLMFactory and stream tokens back using SSE
"""

import logging
from uuid import UUID
from fastapi import APIRouter, Header, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.gateway import ChatPayload
from app.services.kernel import AimosKernel
from app.services.progress import get_or_create_test_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/chat",
    summary="Stream AI Mentor Response",
    description=(
        "Accepts a student message and the active curriculum node, injects "
        "pedagogical context and Socratic rules, then streams the response."
    ),
    response_description="Server-Sent Events (SSE) token stream from the LLM provider.",
    responses={
        200: {"description": "Streaming SSE response.", "content": {"text/event-stream": {}}},
        400: {"description": "Unsupported LLM provider."},
        401: {"description": "Upstream API key authentication failed."},
        404: {"description": "Curriculum node not found."},
        422: {"description": "Invalid request payload."},
        500: {"description": "Internal gateway error."},
    },
    tags=["AI Gateway"],
)
async def stream_mentor_chat(
    payload: ChatPayload,
    x_user_api_key: str = Header(
        ...,
        alias="X-User-API-Key",
        description="The student's personal LLM API token (e.g. nvapi-xxxx).",
    ),
    x_user_provider: str = Header(
        ...,
        alias="X-User-Provider",
        description="Target compute provider (e.g. nvidia-nim).",
    ),
    x_user_id: str | None = Header(
        default=None,
        alias="X-User-Id",
        description="Optional UUID of the user. Falls back to default test user if empty.",
    ),
    authorization: str | None = Header(
        default=None,
        alias="Authorization",
        description="JWT session token (Phase 3).",
    ),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """
    Orchestrated BYOK streaming gateway endpoint.
    Retrieves progress, loads cache, compiles prompt, and returns stream.
    """
    # -------------------------------------------------------------------------
    # 1. Resolve Executing User UUID (Fallback to Seed User in Dev)
    # -------------------------------------------------------------------------
    user_uuid = None
    if x_user_id:
        try:
            user_uuid = UUID(x_user_id.strip())
        except ValueError:
            logger.warning("Invalid X-User-Id header value: '%s'. Using test user.", x_user_id)

    if not user_uuid:
        user_uuid = await get_or_create_test_user(db)

    # -------------------------------------------------------------------------
    # 2. Stream AI Response through central AI-MOS Kernel (Problem 2)
    # -------------------------------------------------------------------------
    event_stream = await AimosKernel.stream_socratic_chat(
        db=db,
        user_uuid=user_uuid,
        node_id=payload.current_node_id,
        payload=payload.model_dump(),
        provider=x_user_provider,
        api_key=x_user_api_key,
        behavior_type="teaching"
    )

    async def event_stream_generator():
        try:
            async for chunk in event_stream:
                if chunk:
                    yield chunk.encode("utf-8")
        except Exception as exc:
            logger.error("SSE stream interrupted: %s", type(exc).__name__)

    return StreamingResponse(
        content=event_stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
