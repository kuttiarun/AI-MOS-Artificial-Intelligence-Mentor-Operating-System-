"""
AI-MOS Backend — Curriculum Endpoints
======================================
Provides routes for fetching curriculum lessons and validating student
explanations to unlock syllabus gates.

In Phase 4, the validation route is completely integrated with:
- Socratic Evaluator (LLM Socratic grader)
- PostgreSQL progress tracker and weakness metrics
- Single transaction safety block (ensuring complete rollback on error)
"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.knowledge_base import KnowledgeBaseService
from app.services.evaluator import SocraticEvaluator
from app.services.progress import (
    get_or_create_test_user,
    get_curriculum_node,
    get_user_node_progress,
    upsert_user_progress,
    unlock_next_nodes,
    resolve_weakness_record,
    record_validation_failure,
    increment_streak,
    CurriculumNode,
    UserProgress,
)
from sqlalchemy import select

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Request/Response Schemas
# =============================================================================

class NodeContentResponse(BaseModel):
    id: str
    title: str
    content: str


class NodeProgressItem(BaseModel):
    id: str
    title: str
    phase: int
    status: str  # "locked" | "unlocked" | "in_progress" | "completed"


class ValidateRequest(BaseModel):
    node_id: str = Field(..., description="The curriculum node being validated.")
    submission_type: str = Field(..., description="Type: 'explanation' or 'code'")
    user_text: str = Field(..., min_length=1, description="The student's submission text.")


class ValidateResponse(BaseModel):
    passed: bool
    confidence_score: int
    feedback: str
    next_node_id: str | None


# =============================================================================
# GET /node/{node_id}
# =============================================================================
@router.get(
    "/node/{node_id}",
    summary="Get Curriculum Node Content",
    response_model=NodeContentResponse,
    tags=["Curriculum"],
)
async def get_node_contents(
    node_id: str,
    db: AsyncSession = Depends(get_db),
) -> NodeContentResponse:
    """
    Retrieves the details and markdown curriculum content for a specific node.
    """
    node = await get_curriculum_node(db, node_id)
    if not node:
        logger.warning("Curriculum node not found on content lookup: %s", node_id)
        raise HTTPException(
            status_code=404,
            detail=f"Curriculum node '{node_id}' does not exist."
        )

    # Load content from async cache file engine
    content = await KnowledgeBaseService.get_lesson_content(node.content_path)

    return NodeContentResponse(
        id=node.id,
        title=node.title,
        content=content,
    )


# =============================================================================
# GET /progress
# =============================================================================
@router.get(
    "/progress",
    summary="Get Full Curriculum Progress for User",
    response_model=list[NodeProgressItem],
    tags=["Curriculum"],
)
async def get_curriculum_progress(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    db: AsyncSession = Depends(get_db),
) -> list[NodeProgressItem]:
    """
    Returns all curriculum nodes with the requesting user's live progress
    status. Used by the CurriculumTree frontend component to render live
    node state (locked / unlocked / in_progress / completed).
    """
    # Resolve user UUID
    user_uuid = None
    if x_user_id:
        try:
            user_uuid = UUID(x_user_id.strip())
        except ValueError:
            logger.warning("Invalid X-User-Id in progress request: '%s'. Using test user.", x_user_id)
    if not user_uuid:
        user_uuid = await get_or_create_test_user(db)

    # Fetch all curriculum nodes ordered by phase
    nodes_result = await db.execute(
        select(CurriculumNode).order_by(CurriculumNode.phase, CurriculumNode.id)
    )
    all_nodes = nodes_result.scalars().all()

    # Fetch all progress records for this user in one query
    progress_result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user_uuid)
    )
    progress_records = {p.node_id: p.status for p in progress_result.scalars().all()}

    # Build response — default to 'locked' for nodes with no progress record
    result = [
        NodeProgressItem(
            id=node.id,
            title=node.title,
            phase=node.phase,
            status=progress_records.get(node.id, "locked"),
        )
        for node in all_nodes
    ]
    return result


# =============================================================================
# POST /validate
# =============================================================================
@router.post(
    "/validate",
    summary="Validate Student Understanding Gate",
    response_model=ValidateResponse,
    tags=["Curriculum"],
)
async def validate_node_submission(
    request: ValidateRequest,
    x_user_api_key: str = Header(
        ...,
        alias="X-User-API-Key",
        description="The student's personal LLM API token for grading call.",
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
    db: AsyncSession = Depends(get_db),
) -> ValidateResponse:
    """
    Evaluates a student's explanation against the node's learning goals.
    Updates the database within a single transaction session block.
    """
    # 1. Resolve Executing User UUID
    user_uuid = None
    if x_user_id:
        try:
            user_uuid = UUID(x_user_id.strip())
        except ValueError:
            logger.warning("Invalid X-User-Id header value: '%s'. Using test user.", x_user_id)

    if not user_uuid:
        user_uuid = await get_or_create_test_user(db)

    # 2. Check if curriculum node exists
    node = await get_curriculum_node(db, request.node_id)
    if not node:
        raise HTTPException(
            status_code=404,
            detail=f"Curriculum node '{request.node_id}' does not exist."
        )

    # 3. Call Socratic Evaluator (incorporating BYOK compute key)
    evaluation = await SocraticEvaluator.evaluate_explanation(
        provider=x_user_provider,
        api_key=x_user_api_key,
        node_id=request.node_id,
        student_text=request.user_text,
    )

    passed = evaluation["passed"]
    score = evaluation["confidence_score"]
    feedback = evaluation["feedback"]

    # -------------------------------------------------------------------------
    # 4. Database Transaction Update Loop (Single Transaction Safety)
    # -------------------------------------------------------------------------
    try:
        # Wrap all updates in db.begin() only if a transaction is not already active
        if db.in_transaction():
            if passed:
                # Upgrading node to completed status
                await upsert_user_progress(db, user_uuid, request.node_id, "completed", score)
                # Unlocking dependents/child nodes
                unlocked_nodes = await unlock_next_nodes(db, user_uuid, request.node_id)
                # Resolving any active weaknesses on this topic
                await resolve_weakness_record(db, user_uuid, request.node_id)
                
                # Determine next node to unlock (if any)
                next_node_id = unlocked_nodes[0].node_id if unlocked_nodes else None
            else:
                # Setting node to active studying state
                await upsert_user_progress(db, user_uuid, request.node_id, "in_progress", score)
                # Logging weakness parameters or failure count
                await record_validation_failure(db, user_uuid, request.node_id)
                
                next_node_id = None
        else:
            async with db.begin():
                if passed:
                    await upsert_user_progress(db, user_uuid, request.node_id, "completed", score)
                    unlocked_nodes = await unlock_next_nodes(db, user_uuid, request.node_id)
                    await resolve_weakness_record(db, user_uuid, request.node_id)
                    await increment_streak(db, user_uuid)  # 🔥 update streak on success
                    next_node_id = unlocked_nodes[0].node_id if unlocked_nodes else None
                else:
                    # Setting node to active studying state
                    await upsert_user_progress(db, user_uuid, request.node_id, "in_progress", score)
                    # Logging weakness parameters or failure count
                    await record_validation_failure(db, user_uuid, request.node_id)
                    
                    next_node_id = None

    except Exception as exc:
        logger.error("Database transaction failed during checkpoint validate: %s", str(exc))
        # Roll back is handled automatically by the 'async with db.begin()' block.
        raise HTTPException(
            status_code=500,
            detail="An error occurred while updating the learning progress state."
        )

    return ValidateResponse(
        passed=passed,
        confidence_score=score,
        feedback=feedback,
        next_node_id=next_node_id,
    )
