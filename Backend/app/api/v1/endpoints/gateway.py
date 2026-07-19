"""
AI-MOS Backend — AI Gateway Endpoint
======================================
Implements POST /api/v1/gateway/chat — the core BYOK streaming route.

Data flow (SRS §1):
  1. Authenticate session JWT (TODO: Phase 3 — stub pass-through for Phase 1)
  2. Validate ChatPayload (prompt injection sanitized by Pydantic validator)
  3. Fetch curriculum context for the active node (stub → Phase 2 Markdown engine)
  4. Assemble the strict pedagogical system prompt (Research Coach / MOD-05)
  5. Delegate to LLMFactory with user's own API key
  6. Stream raw SSE tokens back to the frontend

Security invariants (SRS §4):
  - X-User-API-Key is NEVER written to logs, DB, or response bodies.
  - Upstream 401 errors are caught and returned as structured JSON.
  - Prompt injection strings are stripped by the ChatPayload validator.
"""

import logging

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.gateway import ChatPayload
from app.services.llm_factory import LLMFactory

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Curriculum Context Provider (Phase 1 Stub)
# =============================================================================
# TODO (Phase 2 — Day 5/6): Replace this stub with the async Markdown
# file reader that loads lesson content from the local knowledge base
# based on node_id. The context assembler will also merge the user's
# active weakness flags from the `weak_areas` table.
def get_curriculum_context(node_id: str) -> str:
    """
    Phase 1 stub: returns a placeholder context string for the given node.

    In Phase 2, this will:
      1. Read the Markdown lesson file at `curriculum_nodes.content_path`
      2. Fetch the user's weak areas from `weak_areas` table
      3. Return a rich, assembled context block
    """
    return (
        f"[Curriculum Module: {node_id}] "
        "The student is currently studying this topic. "
        "Guide them using the Socratic method without providing complete solutions."
    )


# =============================================================================
# Pedagogical System Prompt Builder (MOD-05: Research Coach)
# =============================================================================
def build_pedagogical_prompt(lesson_context: str) -> str:
    """
    Constructs the strict pedagogical boundary system prompt that enforces
    the Research Coach rules defined in PRD MOD-05 and Architecture.md.

    This prompt is the core of the AI-MOS educational philosophy:
    - Teach WHY before HOW
    - Never hand out copy-pasteable code on first attempt
    - Use analogies and Socratic questioning
    - Point to documentation rather than giving direct answers
    """
    return (
        f"{lesson_context}\n\n"
        "You are the AI-MOS software engineering mentor. "
        "You are a world-class educator who believes deeply in first-principles thinking. "
        "Adhere to the following rules with absolute precision:\n\n"
        "PEDAGOGICAL RULES:\n"
        "1. SOCRATIC METHOD: Never give a direct answer. Instead, ask targeted guiding "
        "questions that lead the student to discover the answer themselves.\n"
        "2. NO COMPLETE CODE: You are STRICTLY PROHIBITED from providing complete, "
        "copy-pasteable, executable code blocks on the student's first attempt at any problem. "
        "Provide structural pseudocode or partial skeletons only.\n"
        "3. ANALOGY FIRST: Frame every concept explanation around a real-world analogy "
        "before introducing technical terminology.\n"
        "4. DOCUMENTATION HINTS: When a student is stuck, direct them to the official "
        "documentation (e.g., 'Check the Java Collections Framework Javadoc for HashMap') "
        "rather than summarizing it for them.\n"
        "5. VERIFY UNDERSTANDING: Before advancing to a new concept, ask the student to "
        "explain what they just learned in their own words.\n"
        "6. FIRST PRINCIPLES: Always explain WHY a concept exists before HOW to use it. "
        "Connect every technical decision to the real-world problem it solves.\n"
        "7. ENCOURAGE RESEARCH: When the student asks a factual question you could answer "
        "directly, instead give them a targeted search query or resource path to find it "
        "themselves, building their independent research skills."
    )


# =============================================================================
# Route: POST /chat
# =============================================================================
@router.post(
    "/chat",
    summary="Stream AI Mentor Response",
    description=(
        "Accepts a student message and the active curriculum node, injects "
        "pedagogical context and Research Coach constraints, then streams the "
        "AI mentor's response using the student's own LLM API key."
    ),
    response_description="Server-Sent Events (SSE) token stream from the LLM provider.",
    responses={
        200: {"description": "Streaming SSE response.", "content": {"text/event-stream": {}}},
        400: {"description": "Unsupported LLM provider."},
        401: {"description": "Upstream API key authentication failed."},
        422: {"description": "Invalid request payload."},
        500: {"description": "Internal gateway error."},
    },
    tags=["AI Gateway"],
)
async def stream_mentor_chat(
    payload: ChatPayload,
    # -------------------------------------------------------------------------
    # BYOK Headers (SRS §3)
    # X-User-API-Key: The student's personal LLM developer token.
    #   - Validated by the upstream provider, never by our server.
    #   - NEVER logged, stored, or included in any response body.
    # X-User-Provider: Identifies the target compute provider.
    #   - Determines which LLMFactory branch handles the request.
    # -------------------------------------------------------------------------
    x_user_api_key: str = Header(
        ...,
        alias="X-User-API-Key",
        description=(
            "The student's personal LLM API token (e.g., nvapi-xxxx). "
            "Processed in-memory only. Never persisted."
        ),
    ),
    x_user_provider: str = Header(
        ...,
        alias="X-User-Provider",
        description="Target compute provider (e.g., nvidia-nim, openai).",
    ),
    # -------------------------------------------------------------------------
    # TODO (Phase 3 — Day 3): Replace this with a real JWT dependency:
    # current_user: User = Depends(get_current_user)
    # For Phase 1 we accept and ignore the Authorization header to keep
    # the gateway structurally correct without blocking integration tests.
    # -------------------------------------------------------------------------
    authorization: str | None = Header(
        default=None,
        alias="Authorization",
        description="JWT session token. Required from Phase 3 onwards.",
        include_in_schema=True,
    ),
) -> StreamingResponse:
    """
    Core BYOK streaming gateway endpoint.

    Orchestrates the full AI-MOS request pipeline:
      curriculum context → pedagogical prompt → LLM stream → SSE response
    """
    # -------------------------------------------------------------------------
    # TODO (Phase 3): Verify JWT and extract user_id from the token.
    # Example:
    #   user_id = await verify_session_token(authorization)
    #   user_state = await get_user_state(db, user_id)
    # -------------------------------------------------------------------------

    # Step 1: Gather curriculum context for the active lesson node
    # (Phase 2 will replace this with real DB + Markdown file lookups)
    lesson_context = get_curriculum_context(payload.current_node_id)

    # Step 2: Build the strict pedagogical system prompt (MOD-05)
    system_prompt = build_pedagogical_prompt(lesson_context)

    # Step 3: Delegate to the LLM factory (uses user's key, never ours)
    # The api_key variable exists only in this stack frame.
    provider_response = await LLMFactory.get_streaming_response(
        provider=x_user_provider,
        api_key=x_user_api_key,  # SRS §4: zero credential retention
        payload=payload.model_dump(),
        system_prompt=system_prompt,
    )

    # Step 4: Wrap the raw httpx stream in an async generator
    # and stream it back to the browser as SSE.
    async def event_stream_generator():
        """
        Yields raw byte chunks from the upstream SSE response.
        The httpx response is properly closed when the generator exits,
        even if the client disconnects mid-stream.
        """
        try:
            async for chunk in provider_response.aiter_raw():
                if chunk:
                    yield chunk
        except Exception as exc:
            logger.error(
                "Stream interrupted for node '%s': %s",
                payload.current_node_id,
                type(exc).__name__,
                # Intentionally NOT logging api_key or provider details
            )
        finally:
            # Always close the upstream connection regardless of outcome
            await provider_response.aclose()

    return StreamingResponse(
        content=event_stream_generator(),
        media_type="text/event-stream",
        headers={
            # Standard SSE headers for browser EventSource compatibility
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering for streaming
            "Connection": "keep-alive",
        },
    )
