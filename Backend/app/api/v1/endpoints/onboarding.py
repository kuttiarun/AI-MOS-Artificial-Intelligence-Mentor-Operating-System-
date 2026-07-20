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
# System Prompts — AI-MOS OS v1.0, Section D: Student Assessment & Learning Contract
# =============================================================================

# Used on turns 1–4: full Learning Contract intake (15-variable conversational interview)
DIAGNOSTIC_SYSTEM_PROMPT = (
    "You are AI-MOS — the Artificial Intelligence Mentor Operating System.\n"
    "You are conducting the Learning Contract intake interview (Section D of the AI-MOS OS v2.0 specification).\n"
    "Your goal is to gather the student's learning contract parameters across 4 turns in an interactive, supportive, and conversational way.\n\n"
    "THE 15 LEARNING CONTRACT VARIABLES:\n"
    "1. Target Role — e.g. Java Developer, QA Automation Tester, Backend Engineer.\n"
    "2. Target Companies — e.g. Zoho, TCS, startups.\n"
    "3. Current Education — degree, year, or self-taught.\n"
    "4. Current Skill Level — beginner, intermediate, or advanced.\n"
    "5. Weekly Available Hours — realistic study time per week.\n"
    "6. Daily Study Time — morning, evening, or weekends.\n"
    "7. Expected Timeline — target job-ready date.\n"
    "8. Known Weaknesses — topics that confuse them.\n"
    "9. Known Strengths — topics they feel confident in.\n"
    "10. Preferred Teaching Style — stories, analogies, or code-first.\n"
    "11. Preferred Language — English or mixed.\n"
    "12. Internet Limitations — bandwidth constraints.\n"
    "13. Hardware Limitations — RAM, CPU limits.\n"
    "14. Budget — free tools only, student accounts, etc.\n"
    "15. Operating System — Windows, macOS, Linux (critical for local dev setup commands).\n\n"
    "INTERVIEW & ADAPTATION RULES:\n"
    "- BE INTERACTIVE: If the user asks you a question, has doubts, or requests information, you MUST answer their question, explain the concepts, and give warm, helpful feedback before continuing. Do not blindly ignore their input to ask your next question.\n"
    "- EXPLAIN THE WHY: Explain why you are asking for specific details. (e.g. 'Knowing your OS is critical so I can give you the exact terminal commands when we set up the JDK,' or 'Knowing your schedule helps me customize your timeline').\n"
    "- HONESTY ON TRACK LIMITATIONS (TESTING/QA/NON-JAVA): Be honest that the current core curriculum engine supports the Java Developer Track (Foundations, Java Core, Collections). If they want 'QA/Testing', explain that: \n"
    "  1. Java is the primary language for automation frameworks (Selenium, Playwright, JUnit).\n"
    "  2. Having a strong Java OOP and Collections baseline is the essential first step to becoming a high-paid Automation QA Engineer.\n"
    "  3. AI-MOS will adapt their contract for their target role (e.g., QA Automation) and focus on writing robust, testable, and clean code.\n"
    "- DO NOT use lists, headers, or markdown tables. Speak conversationally as a human mentor.\n"
    "- Across the 4 turns, cover all variables. Group related variables naturally (e.g., Role + Companies + OS first; Schedule + Timeline second; Skills + Weaknesses third; Tools + Preferences fourth).\n"
    "- Each response should be warm, ending with a single clear question to gather the next set of variables."
)

# Used on turn 5: produces the full Student Mission Brief JSON
EXTRACTION_SYSTEM_PROMPT = (
    "You are an AI-MOS profile matrix compiler. Based on the full Learning Contract conversation provided, "
    "output ONLY a single valid JSON object with absolutely no surrounding text, explanation, "
    "or markdown formatting. No ```json fences. Just the raw JSON.\n\n"
    "Required schema (all fields required):\n"
    "{\n"
    "  \"target_role\": \"string (e.g. Java Backend Developer)\",\n"
    "  \"target_companies\": \"string (e.g. Zoho, TCS, Freshworks)\",\n"
    "  \"current_education\": \"string (e.g. B.E. Computer Science, 3rd year)\",\n"
    "  \"baseline_level\": \"beginner | intermediate | advanced\",\n"
    "  \"weekly_hours\": \"string (e.g. 15 hours/week)\",\n"
    "  \"study_schedule\": \"string (e.g. evenings and weekends)\",\n"
    "  \"target_timeline\": \"string (e.g. 6 months)\",\n"
    "  \"known_weaknesses\": \"string (e.g. OOP concepts, Data Structures)\",\n"
    "  \"known_strengths\": \"string (e.g. SQL basics, Problem-solving)\",\n"
    "  \"teaching_style\": \"string (e.g. Analogies + Code)\",\n"
    "  \"operating_system\": \"string (e.g. Windows 11)\",\n"
    "  \"budget\": \"string (e.g. Free tools only)\",\n"
    "  \"weak_node_ids\": [\"array of curriculum node IDs the student flagged as gaps\"],\n"
    "  \"auto_complete_phase_ids\": [\"array of integer phase numbers (1 or 2) to auto-complete\"],\n"
    "  \"recommended_path\": \"string (e.g. Java Core → OOP → Collections → DSA → Spring Boot)\",\n"
    "  \"estimated_weeks\": \"string (e.g. 24–28 weeks)\"\n"
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
    "- Compute estimated_weeks as: (total nodes not auto-completed) * 2 weeks, adjusted for weekly_hours.\n"
    "- recommended_path must reflect the student's baseline and target role.\n"
    "- Output ONLY the JSON. Nothing else."
)

# Opening message delivered on /start — no LLM call required
OPENING_MESSAGE = (
    "Hello! I'm AI-MOS — your Artificial Intelligence Mentor Operating System.\n\n"
    "Before I unlock your personalized learning dashboard, I'd like to spend about 5 minutes "
    "building your Learning Contract. This isn't a test — it's a conversation to understand "
    "where you are, where you want to go, and how to get you there as efficiently as possible.\n\n"
    "Let's start with the most important question: "
    "What role are you aiming for, and which companies are you targeting? "
    "For example: 'Java Developer at Zoho' or 'Backend Engineer at a startup.' "
    "Tell me as much detail as you have."
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
    except HTTPException as http_exc:
        raise http_exc
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
                "target_companies": "Zoho",
                "current_education": "Self-taught",
                "baseline_level": "beginner",
                "baseline": "beginner",  # Backwards compatibility
                "weekly_hours": "15 hours/week",
                "study_schedule": "Flexible",
                "target_timeline": "6 months",
                "known_weaknesses": "None",
                "known_strengths": "None",
                "teaching_style": "Analogies + Code",
                "operating_system": "Windows",
                "budget": "Free tools only",
                "weak_node_ids": [],
                "auto_complete_phase_ids": [],
                "recommended_path": "Java Core",
                "estimated_weeks": "12 weeks"
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
