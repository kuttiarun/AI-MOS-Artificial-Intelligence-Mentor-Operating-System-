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
from app.services.llm_factory import LLMFactory
from app.services.knowledge_base import KnowledgeBaseService
from app.services.prompt_compiler import PromptCompiler
from app.services.progress import (
    get_or_create_test_user,
    get_user_node_progress,
    get_node_weakness,
    get_active_weak_areas,
    get_curriculum_node,
)

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
    # 2. Fetch Curriculum Node metadata (to get content_path)
    # -------------------------------------------------------------------------
    node = await get_curriculum_node(db, payload.current_node_id)
    if not node:
        logger.warning("Requested curriculum node not found in DB: %s", payload.current_node_id)
        raise HTTPException(
            status_code=404,
            detail=f"Curriculum node '{payload.current_node_id}' does not exist."
        )

    # -------------------------------------------------------------------------
    # 3. Load curriculum markdown content (Async with Caching)
    # -------------------------------------------------------------------------
    lesson_content = await KnowledgeBaseService.get_lesson_content(node.content_path)

    # -------------------------------------------------------------------------
    # 4. Fetch User State & Weaknesses from database
    # -------------------------------------------------------------------------
    # Get current node progress status & confidence
    progress = await get_user_node_progress(db, user_uuid, payload.current_node_id)
    confidence = progress.confidence_score if progress else 0

    # Get failure count for the current node
    weakness = await get_node_weakness(db, user_uuid, payload.current_node_id)
    failures = weakness.failure_count if weakness else 0

    # Get other active weaknesses to construct the struggles list
    all_weaknesses = await get_active_weak_areas(db, user_uuid)

    # -------------------------------------------------------------------------
    # 5. Compile Prompt
    # -------------------------------------------------------------------------
    system_prompt = PromptCompiler.compile_system_prompt(
        lesson_content=lesson_content,
        node_id=payload.current_node_id,
        confidence_score=confidence,
        failure_count=failures,
        active_weaknesses=all_weaknesses,
    )

    # -------------------------------------------------------------------------
    # 6. Contact upstream LLM & stream tokens
    # -------------------------------------------------------------------------
    provider_response = await LLMFactory.get_streaming_response(
        provider=x_user_provider,
        api_key=x_user_api_key,
        payload=payload.model_dump(),
        system_prompt=system_prompt,
    )

    async def event_stream_generator():
        try:
            async for chunk in provider_response.aiter_raw():
                if chunk:
                    yield chunk
        except Exception as exc:
            logger.error("SSE stream interrupted: %s", type(exc).__name__)
        finally:
            await provider_response.aclose()

    return StreamingResponse(
        content=event_stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
