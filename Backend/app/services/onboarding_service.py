"""
AI-MOS Backend — Onboarding Profile Matrix Transaction Service
==============================================================
Consumes the LLM-generated diagnostic profile matrix from Module 01
and applies it atomically to the database:

  1. Updates user's target_role and operating_system in `users`.
  2. Auto-completes curriculum phases based on prior knowledge baseline.
  3. Unlocks the first node of the next phase for the student to begin.
  4. Seeds initial weak_areas entries for flagged knowledge gaps.
  5. Sets onboarding_complete = TRUE to unlock the main dashboard.

Design principles:
  - Single async transaction — full rollback on any failure.
  - Re-uses existing progress.py helpers to stay DRY.
  - Phase auto-complete is capped at Phase 2 (never skips Phase 3+
    Collections to enforce minimum rigor, as per PRD MOD-01).
"""

import logging
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.progress import (
    CurriculumNode,
    User,
    upsert_user_progress,
    record_validation_failure,
)

logger = logging.getLogger(__name__)

# Maximum phase that can be auto-completed based on prior knowledge.
# Phase 3 (Collections) and above must always be earned through the system.
MAX_AUTO_COMPLETE_PHASE = 2


async def apply_profile_matrix(
    db: AsyncSession,
    user_uuid: UUID,
    matrix: dict,
) -> None:
    """
    Applies the onboarding diagnostic profile matrix to the database.

    Args:
        db:          Active async database session (caller manages transaction).
        user_uuid:   UUID of the user being onboarded.
        matrix:      Parsed profile dict with the following keys:
                       - target_role (str)
                       - operating_system (str)
                       - baseline (str): "beginner" | "intermediate" | "advanced"
                       - weak_node_ids (list[str])
                       - auto_complete_phase_ids (list[int])
    """
    target_role = matrix.get("target_role", "Java Developer (Zoho)")
    operating_system = matrix.get("operating_system", "Windows")
    raw_auto_phases: list[int] = matrix.get("auto_complete_phase_ids", [])
    weak_node_ids: list[str] = matrix.get("weak_node_ids", [])

    # Enforce the phase cap — never auto-complete Phase 3+
    auto_phases = sorted([
        p for p in raw_auto_phases if isinstance(p, int) and p <= MAX_AUTO_COMPLETE_PHASE
    ])

    logger.info(
        "Applying onboarding matrix for user %s | role=%s | os=%s | auto_phases=%s | weak_nodes=%s",
        user_uuid, target_role, operating_system, auto_phases, weak_node_ids
    )

    # -------------------------------------------------------------------------
    # 1. Update user profile fields
    # -------------------------------------------------------------------------
    await db.execute(
        update(User)
        .where(User.id == user_uuid)
        .values(target_role=target_role, operating_system=operating_system)
    )
    logger.info("Updated profile for user %s → role=%s, os=%s", user_uuid, target_role, operating_system)

    # -------------------------------------------------------------------------
    # 2. Auto-complete all nodes in the designated phases
    # -------------------------------------------------------------------------
    max_completed_phase = 0
    for phase_id in auto_phases:
        nodes_result = await db.execute(
            select(CurriculumNode).where(CurriculumNode.phase == phase_id)
        )
        nodes = nodes_result.scalars().all()

        for node in nodes:
            await upsert_user_progress(
                db, user_uuid, node.id,
                status="completed",
                confidence_score=8,  # Baseline competency level for prior knowledge
            )

        if nodes:
            max_completed_phase = max(max_completed_phase, phase_id)
            logger.info("Auto-completed %d node(s) in Phase %d for user %s", len(nodes), phase_id, user_uuid)

    # -------------------------------------------------------------------------
    # 3. Unlock the first node of the next phase after auto-completed ones
    # -------------------------------------------------------------------------
    if max_completed_phase > 0:
        next_phase = max_completed_phase + 1
        next_phase_result = await db.execute(
            select(CurriculumNode)
            .where(CurriculumNode.phase == next_phase)
            .order_by(CurriculumNode.id)
            .limit(1)
        )
        next_node = next_phase_result.scalars().first()
        if next_node:
            await upsert_user_progress(db, user_uuid, next_node.id, status="unlocked", confidence_score=0)
            logger.info("Unlocked entry node '%s' (Phase %d) for user %s", next_node.id, next_phase, user_uuid)
    else:
        # Beginner baseline: unlock the very first curriculum node
        first_node_result = await db.execute(
            select(CurriculumNode)
            .where(CurriculumNode.prerequisite_id.is_(None))
            .limit(1)
        )
        first_node = first_node_result.scalars().first()
        if first_node:
            await upsert_user_progress(db, user_uuid, first_node.id, status="unlocked", confidence_score=0)
            logger.info("Unlocked root node '%s' for beginner user %s", first_node.id, user_uuid)

    # -------------------------------------------------------------------------
    # 4. Seed identified knowledge gaps into weak_areas
    # -------------------------------------------------------------------------
    for node_id in weak_node_ids:
        # Verify the node exists before seeding — avoids FK violations on LLM hallucinations
        node_check = await db.execute(
            select(CurriculumNode).where(CurriculumNode.id == node_id)
        )
        if node_check.scalars().first():
            await record_validation_failure(db, user_uuid, node_id)
            logger.info("Seeded weak_areas entry for node '%s' for user %s", node_id, user_uuid)
        else:
            logger.warning("Onboarding matrix referenced unknown node_id '%s' — skipping weak seed.", node_id)

    # -------------------------------------------------------------------------
    # 5. Mark onboarding as complete — unlocks the main dashboard
    # -------------------------------------------------------------------------
    await db.execute(
        update(User)
        .where(User.id == user_uuid)
        .values(onboarding_complete=True)
    )
    logger.info("Onboarding complete for user %s. Dashboard unlocked.", user_uuid)
