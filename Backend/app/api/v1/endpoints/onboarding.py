"""
AI-MOS Backend — Module 01: Onboarding Diagnostic Endpoints
=============================================================
Implements the AI-driven diagnostic interview that runs before the
student accesses the main curriculum dashboard.

The diagnostic flow:
  1. POST /start  → Returns the opening question. No LLM call needed.
  2. POST /chat   → Handles each message turn (stateless — client carries history).
                    On turn 5, forces JSON profile extraction and commits the
                    full profile matrix to the database atomically.
  3. GET  /status → Checks if the user has completed onboarding. Used by the
                    frontend to gate the main dashboard.

Stream Parsing:
  Uses the existing LLMFactory.extract_content_from_stream accumulator and
  the greedy curly-brace substring parser (same pattern as interview.py).

Stateless Design:
  Mirrors the interview.py stateless pattern — the client sends the full
  chat_history array on every /chat request. The backend never stores
  conversation state between turns.
"""

import json
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.llm_factory import LLMFactory
from app.services.progress import User, get_or_create_test_user
from app.services.onboarding_service import apply_profile_matrix

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Request / Response Schemas
# =============================================================================

class OnboardingStartResponse(BaseModel):
    session_id: str
    opening_message: str


class OnboardingMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class OnboardingChatRequest(BaseModel):
    turn_number: int = Field(..., ge=1, le=5, description="Current turn index (1–5).")
    message: str = Field(..., min_length=1, description="The user's response text.")
    chat_history: list[OnboardingMessage] = Field(
        default=[],
        description="Full conversation history so far (stateless — client carries this)."
    )


class OnboardingChatResponse(BaseModel):
    reply: str = Field(..., description="The diagnostic interviewer's next message or final summary.")
    turn_number: int
    is_complete: bool = Field(..., description="True on turn 5 after profile is committed.")
    profile_matrix: dict | None = Field(None, description="Extracted profile on final turn only.")


class OnboardingStatusResponse(BaseModel):
    onboarding_complete: bool


# =============================================================================
# System Prompts
# =============================================================================

# Used on turns 1–4: pure diagnostic interview mode
DIAGNOSTIC_SYSTEM_PROMPT = (
    "You are an expert software engineering coach conducting a structured diagnostic interview "
    "to build a personalized learning profile for a student.\n\n"
    "RULES:\n"
    "- Ask exactly ONE focused, open-ended question per turn.\n"
    "- Do NOT teach, explain, or provide feedback on their answers.\n"
    "- Do NOT use lists, headers, or markdown — speak conversationally.\n"
    "- Topics to cover across 4 turns: prior programming experience, target job role "
    "(e.g. Java Developer at Zoho), operating system they use, and any specific Java or "
    "data structure topics they already know or feel weak on.\n"
    "- Keep each question brief (1–2 sentences max).\n"
    "- After they answer, immediately pivot with your next diagnostic question."
)

# Used on turn 5: forces structured JSON profile matrix output
EXTRACTION_SYSTEM_PROMPT = (
    "You are a profile matrix compiler. Based on the full diagnostic conversation provided, "
    "output ONLY a single valid JSON object with absolutely no surrounding text, explanation, "
    "or markdown formatting. No ```json fences. Just the raw JSON.\n\n"
    "Required schema:\n"
    "{\n"
    "  \"target_role\": \"string (e.g. Java Developer (Zoho))\",\n"
    "  \"operating_system\": \"string (e.g. Windows, Ubuntu, macOS)\",\n"
    "  \"baseline\": \"beginner | intermediate | advanced\",\n"
    "  \"weak_node_ids\": [\"array of curriculum node IDs the student flagged as gaps\"],\n"
    "  \"auto_complete_phase_ids\": [\"array of integer phase numbers (1 or 2) to auto-complete\"]\n"
    "}\n\n"
    "Valid curriculum node IDs for weak_node_ids:\n"
    "  foundations-intro, foundations-how-computers-work, foundations-programming-basics,\n"
    "  java-core-setup, java-core-oop-classes, java-core-oop-inheritance, java-core-interface,\n"
    "  java-core-abstract-class, java-collections-arrays, java-collections-arraylist,\n"
    "  java-collections-linkedlist, java-collections-hashmap\n\n"
    "Rules:\n"
    "- Only include node IDs from the list above. Do not invent new IDs.\n"
    "- auto_complete_phase_ids must only contain 1 or 2 (never 3+).\n"
    "- A 'beginner' has auto_complete_phase_ids: []\n"
    "- An 'intermediate' typically has auto_complete_phase_ids: [1]\n"
    "- An 'advanced' user has auto_complete_phase_ids: [1, 2]\n"
    "- Output ONLY the JSON. Nothing else."
)

# Opening message delivered on /start — no LLM call required
OPENING_MESSAGE = (
    "Hello! I'm your AI-MOS diagnostic advisor. Before we unlock your personalized learning "
    "dashboard, I'd like to ask you a few quick questions to tailor your curriculum path. "
    "This will only take about 5 minutes.\n\n"
    "Let's start: Have you done any programming before, and if so, what languages or "
    "projects have you worked with?"
)


# =============================================================================
# POST /start
# =============================================================================
@router.post(
    "/start",
    summary="Initialize Onboarding Diagnostic Session",
    response_model=OnboardingStartResponse,
    tags=["Onboarding"],
)
async def start_onboarding() -> OnboardingStartResponse:
    """
    Returns the opening diagnostic question. No LLM call or DB write is needed —
    the opening message is static and consistent for all users.
    """
    return OnboardingStartResponse(
        session_id="onboarding_session_v1",
        opening_message=OPENING_MESSAGE,
    )


# =============================================================================
# POST /chat
# =============================================================================
@router.post(
    "/chat",
    summary="Submit Diagnostic Turn and Advance Conversation",
    response_model=OnboardingChatResponse,
    tags=["Onboarding"],
)
async def onboarding_chat_turn(
    request: OnboardingChatRequest,
    x_user_api_key: str = Header(..., alias="X-User-API-Key"),
    x_user_provider: str = Header(..., alias="X-User-Provider"),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    db: AsyncSession = Depends(get_db),
) -> OnboardingChatResponse:
    """
    Handles each turn of the diagnostic conversation.

    Turns 1–4: LLM continues the interview with DIAGNOSTIC_SYSTEM_PROMPT.
    Turn 5:    LLM switches to EXTRACTION_SYSTEM_PROMPT, producing a JSON
               profile matrix which is parsed and committed to the database.
    """
    # 1. Resolve user identity
    user_uuid = None
    if x_user_id:
        try:
            user_uuid = UUID(x_user_id.strip())
        except ValueError:
            logger.warning("Invalid X-User-Id '%s' in onboarding — using test user.", x_user_id)
    if not user_uuid:
        user_uuid = await get_or_create_test_user(db)

    # 2. Select system prompt based on turn number
    is_final_turn = (request.turn_number == 5)
    system_prompt = EXTRACTION_SYSTEM_PROMPT if is_final_turn else DIAGNOSTIC_SYSTEM_PROMPT

    # 3. Build the conversation payload for the LLM
    # Include the full history so the model has complete context
    formatted_history = "\n".join([
        f"{msg.role}: {msg.content}" for msg in request.chat_history
    ])
    user_prompt = (
        f"[Conversation so far]\n{formatted_history}\n\n"
        f"[Student's latest response]\n{request.message}"
    )
    if is_final_turn:
        user_prompt += (
            "\n\nBased on the complete conversation above, compile the JSON profile matrix now."
        )

    # 4. Call the LLM via the multi-model factory
    try:
        event_stream = await LLMFactory.get_streaming_response(
            provider=x_user_provider,
            api_key=x_user_api_key,
            payload={"user_message": user_prompt},
            system_prompt=system_prompt,
        )
        response_text = await LLMFactory.extract_content_from_stream(event_stream)
    except Exception as llm_exc:
        logger.error("LLM call failed during onboarding turn %d: %s", request.turn_number, str(llm_exc))
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider error during onboarding: {str(llm_exc)}"
        )

    # -------------------------------------------------------------------------
    # 5. Final Turn: Extract JSON matrix, apply to DB, and complete onboarding
    # -------------------------------------------------------------------------
    if is_final_turn:
        profile_matrix = None
        try:
            # Greedy curly brace extraction — same pattern as interview.py
            first_brace = response_text.find("{")
            last_brace = response_text.rfind("}")

            if first_brace == -1 or last_brace == -1:
                raise ValueError("LLM did not return a valid JSON block in onboarding extraction turn.")

            json_str = response_text[first_brace: last_brace + 1]
            profile_matrix = json.loads(json_str)

        except (ValueError, json.JSONDecodeError) as parse_exc:
            logger.error("Profile matrix extraction failed: %s. Raw response: %s", str(parse_exc), response_text[:500])
            # Fall back to a safe beginner profile to avoid blocking the user
            profile_matrix = {
                "target_role": "Java Developer (Zoho)",
                "operating_system": "Windows",
                "baseline": "beginner",
                "weak_node_ids": [],
                "auto_complete_phase_ids": [],
            }
            logger.warning("Using fallback beginner profile for user %s.", user_uuid)

        # Commit the profile matrix atomically
        try:
            if db.in_transaction():
                await apply_profile_matrix(db, user_uuid, profile_matrix)
            else:
                async with db.begin():
                    await apply_profile_matrix(db, user_uuid, profile_matrix)
        except Exception as db_exc:
            logger.error("Failed to apply onboarding profile matrix for user %s: %s", user_uuid, str(db_exc))
            raise HTTPException(
                status_code=500,
                detail="Failed to save your learning profile. Please try again."
            )

        return OnboardingChatResponse(
            reply=(
                "Excellent! I've built your personalized learning profile. "
                "Your curriculum dashboard is now ready. Let's begin!"
            ),
            turn_number=5,
            is_complete=True,
            profile_matrix=profile_matrix,
        )

    # -------------------------------------------------------------------------
    # 6. Standard Turn: Return interviewer's next diagnostic question
    # -------------------------------------------------------------------------
    return OnboardingChatResponse(
        reply=response_text,
        turn_number=request.turn_number,
        is_complete=False,
        profile_matrix=None,
    )


# =============================================================================
# GET /status
# =============================================================================
@router.get(
    "/status",
    summary="Check User Onboarding Completion Status",
    response_model=OnboardingStatusResponse,
    tags=["Onboarding"],
)
async def get_onboarding_status(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    db: AsyncSession = Depends(get_db),
) -> OnboardingStatusResponse:
    """
    Returns whether the user has completed onboarding.
    Used by the frontend to gate access to the main curriculum dashboard.
    Falls back to incomplete (False) for unknown users to ensure they
    always pass through the diagnostic interview.
    """
    if not x_user_id:
        # No user ID provided — assume onboarding needed
        return OnboardingStatusResponse(onboarding_complete=False)

    try:
        user_uuid = UUID(x_user_id.strip())
    except ValueError:
        return OnboardingStatusResponse(onboarding_complete=False)

    result = await db.execute(
        select(User.onboarding_complete).where(User.id == user_uuid)
    )
    flag = result.scalar_one_or_none()

    if flag is None:
        # User doesn't exist yet — onboarding not done
        return OnboardingStatusResponse(onboarding_complete=False)

    return OnboardingStatusResponse(onboarding_complete=bool(flag))
