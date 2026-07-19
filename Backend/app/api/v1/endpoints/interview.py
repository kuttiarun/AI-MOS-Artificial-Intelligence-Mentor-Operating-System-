"""
AI-MOS Backend — Zoho Mock Interview Simulator
================================================
Implements endpoints for high-pressure Zoho mock interview sessions.

Endpoints:
  - POST /api/v1/interview/start: Kicks off session with Srinivasan.
  - POST /api/v1/interview/chat: Evaluates depth, returns score, increments
    failure logs if score < 6/10, and generates the next pressure question.
"""

import json
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.llm_factory import LLMFactory
from app.services.progress import (
    get_or_create_test_user,
    record_validation_failure,
)
from app.services.evaluator import SocraticEvaluator

logger = logging.getLogger(__name__)

router = APIRouter()

# =============================================================================
# Request/Response Schemas
# =============================================================================

class InterviewStartResponse(BaseModel):
    session_id: str
    interviewer: str
    initial_question: str


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message author ('user' or 'assistant').")
    content: str = Field(..., description="The message content text.")


class InterviewChatRequest(BaseModel):
    node_id: str = Field(..., description="The active curriculum node key.")
    candidate_answer: str = Field(..., description="The candidate's response text.")
    chat_history: list[ChatMessage] = Field(default=[], description="Ongoing array of historical conversation messages.")


class InterviewChatResponse(BaseModel):
    score: int = Field(..., description="Score out of 10.")
    passed: bool = Field(..., description="True if score >= 6.")
    critique: str = Field(..., description="Zoho interviewer's direct feedback.")
    next_question: str = Field(..., description="Follow-up question under pressure.")


# =============================================================================
# Prompts
# =============================================================================

ZOHO_INTERVIEWER_PROMPT = (
    "You are Srinivasan, a Senior Java Architect and Technical Interview Panelist at Zoho "
    "with 15+ years of experience hiring core engineering talent.\n"
    "Your tone is professional, demanding, and highly focused on performance limits and memory layout optimization.\n\n"
    "CRITERIA:\n"
    "Evaluate the candidate's last Java answer. You must output a valid JSON block containing:\n"
    "1. 'score': Integer from 0 to 10 evaluating their technical depth.\n"
    "2. 'passed': Boolean (true if score >= 6, false otherwise).\n"
    "3. 'critique': Direct feedback challenging them or highlighting gaps.\n"
    "4. 'next_question': Srinivasan's next follow-up question, drilling deeper into vtables, heap layouts, "
    "or collection collisions depending on their answer.\n\n"
    "You must return ONLY the JSON block. No conversational text before or after the JSON."
)


# =============================================================================
# Endpoints
# =============================================================================

@router.post(
    "/start",
    summary="Start Zoho Mock Interview Session",
    response_model=InterviewStartResponse,
    tags=["Mock Interview"],
)
async def start_interview() -> InterviewStartResponse:
    """Initializes mock interview with the first core question."""
    initial = (
        "Hello. I am Srinivasan, Senior Architect on the Zoho Java compiler core team. "
        "Let's start. Tell me: how does the JVM manage memory layout differences between "
        "primitive variables and object instances? Be precise about stack frames and heap structures."
    )
    return InterviewStartResponse(
        session_id="zoho_session_dev_01",
        interviewer="Srinivasan (15+ YOE Panelist)",
        initial_question=initial
    )


@router.post(
    "/chat",
    summary="Submit Interview Turn and Score Response",
    response_model=InterviewChatResponse,
    tags=["Mock Interview"],
)
async def interview_chat_turn(
    request: InterviewChatRequest,
    x_user_api_key: str = Header(..., alias="X-User-API-Key"),
    x_user_provider: str = Header(..., alias="X-User-Provider"),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    db: AsyncSession = Depends(get_db),
) -> InterviewChatResponse:
    """
    Submits candidate answer, scores it, writes a failure if score < 6,
    and returns Srinivasan's critique & follow-up question.
    """
    # 1. Resolve user ID
    user_uuid = None
    if x_user_id:
        try:
            user_uuid = UUID(x_user_id.strip())
        except ValueError:
            pass
    if not user_uuid:
        user_uuid = await get_or_create_test_user(db)

    # 2. Formulate evaluation prompt
    formatted_history = "\n".join([f"{msg.role}: {msg.content}" for msg in request.chat_history])
    user_prompt = (
        f"Curriculum Node: {request.node_id}\n"
        f"Candidate Answer: \"{request.candidate_answer}\"\n\n"
        "Here is the history of the conversation so far for context:\n"
        f"{formatted_history}\n\n"
        "Evaluate the candidate's last answer out of 10 and return the JSON response format."
    )

    try:
        # Call the multi-model stream gateway
        event_stream = await LLMFactory.get_streaming_response(
            provider=x_user_provider,
            api_key=x_user_api_key,
            payload={"user_message": user_prompt},
            system_prompt=ZOHO_INTERVIEWER_PROMPT,
        )

        # Accumulate text tokens from the stream
        response_content = await LLMFactory.extract_content_from_stream(event_stream)

        # Parse Srinivasan's JSON response using the outermost brace extractor
        first_brace = response_content.find("{")
        last_brace = response_content.rfind("}")

        if first_brace == -1 or last_brace == -1:
            raise ValueError("Evaluator response is not valid JSON")

        json_str = response_content[first_brace : last_brace + 1]
        result = json.loads(json_str)

        score = int(result.get("score", 5))
        passed = bool(result.get("passed", False))
        critique = str(result.get("critique", "Adequate response. Let's move on."))
        next_q = str(result.get("next_question", "Explain standard hash collision resolutions."))

    except Exception as exc:
        logger.error("Zoho interview evaluator crash: %s. Applying fallback.", str(exc))
        # Fallback values
        score = 5
        passed = False
        critique = "That explanation lacks depth. Zoho engineers must explain memory mechanics."
        next_q = "Explain the memory offset lookups inside the virtual method tables (vtables)."

    # 3. DB Sync: If score < 6/10, increment/insert active failure in weak_areas
    if score < 6:
        logger.info("Candidate failed Zoho check on node %s (score=%d). Logging weakness...", request.node_id, score)
        try:
            # Wrap in atomic write only if a transaction is not already active
            if db.in_transaction():
                await record_validation_failure(db, user_uuid, request.node_id)
            else:
                async with db.begin():
                    await record_validation_failure(db, user_uuid, request.node_id)
        except Exception as db_exc:
            logger.error("Failed to log interview failure count to database: %s", str(db_exc))

    return InterviewChatResponse(
        score=score,
        passed=passed,
        critique=critique,
        next_question=next_q
    )
