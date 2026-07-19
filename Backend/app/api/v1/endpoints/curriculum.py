"""
AI-MOS Backend — Curriculum Endpoints (Phase 1 Stub)
=====================================================
Provides placeholder route structure for the curriculum validation
system described in SRS §3 and Roadmap.md Day 12.

PHASE 1 STATUS: Structural stubs only.

TODO (Phase 4 — Day 12):
  - Implement POST /validate: LLM-driven evaluation of student explanations
  - Update `user_progress.status` and `confidence_score` on pass
  - Create/increment `weak_areas` row on fail
  - Return next_node_id to unlock the next lesson
"""

import logging

from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Request/Response Schemas
# TODO (Phase 4): Move these to app/schemas/curriculum.py
# =============================================================================


class ValidateRequest(BaseModel):
    node_id: str = Field(..., description="The curriculum node being validated.")
    submission_type: str = Field(
        ...,
        description="Type of submission: 'explanation' or 'code'.",
    )
    user_text: str = Field(
        ...,
        min_length=1,
        description="The student's explanation or code submission.",
    )


class ValidateResponse(BaseModel):
    passed: bool
    confidence_score: int
    feedback: str
    next_node_id: str | None


# =============================================================================
# POST /validate
# =============================================================================
@router.post(
    "/validate",
    summary="Validate Student Understanding Gate",
    tags=["Curriculum"],
    response_model=ValidateResponse,
)
async def validate_node_submission(request: ValidateRequest) -> ValidateResponse:
    """
    [PHASE 1 STUB] Evaluates a student's explanation or code submission
    against the curriculum node's learning objectives.

    TODO (Phase 4 implementation):
      1. Retrieve `curriculum_nodes` row for `request.node_id`
      2. Build an evaluation system prompt instructing the LLM to score
         the student's explanation (0-10 confidence_score)
      3. Call LLMFactory with the platform's own evaluation key
         (NOTE: This is NOT the user's BYOK key — this is a platform-side
          evaluation call. Architecture decision to be finalized in Phase 2.)
      4. Parse the LLM JSON response: { passed, confidence_score, feedback }
      5. If passed:
           - UPDATE user_progress SET status='completed', confidence_score=N
           - RETURN next_node_id (from curriculum_nodes.prerequisite tree)
      6. If failed:
           - INSERT/UPDATE weak_areas with failure_count++
           - RETURN feedback with targeted hints
    """
    logger.info("STUB: Validate called for node: %s", request.node_id)
    return ValidateResponse(
        passed=False,
        confidence_score=0,
        feedback=(
            "⚠️ Phase 1 stub: Curriculum validation not yet implemented. "
            "This endpoint will perform LLM-driven understanding evaluation in Phase 4."
        ),
        next_node_id=None,
    )
