"""
AI-MOS Backend — Progress and Weakness Database Selectors & Mutations
=======================================================================
Contains asynchronous database query and update operations utilizing
SQLAlchemy 2.0 select and insert/update statements.

Now includes writing operations (Phase 4):
- upsert_user_progress: inserts/updates a student's node progress state.
- record_validation_failure: increments failure count on concept weakness.
- resolve_weakness_record: marks active weakness as resolved.
- unlock_next_nodes: unlocks child nodes dependent on a prerequisite node.
"""

import logging
from typing import Optional, List
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# Import database metadata
from app.core.database import Base

logger = logging.getLogger(__name__)

# =============================================================================
# Models Mappings
# =============================================================================

class User(Base):
    __tablename__ = "users"

class CurriculumNode(Base):
    __tablename__ = "curriculum_nodes"

class UserProgress(Base):
    __tablename__ = "user_progress"

class WeakArea(Base):
    __tablename__ = "weak_areas"

# Define mappings explicitly
User.id = sa.Column("id", sa.UUID, primary_key=True)
User.email = sa.Column("email", sa.String)
User.password_hash = sa.Column("password_hash", sa.String)
User.target_role = sa.Column("target_role", sa.String)
User.operating_system = sa.Column("operating_system", sa.String)

CurriculumNode.id = sa.Column("id", sa.String, primary_key=True)
CurriculumNode.title = sa.Column("title", sa.String)
CurriculumNode.phase = sa.Column("phase", sa.Integer)
CurriculumNode.prerequisite_id = sa.Column("prerequisite_id", sa.String)
CurriculumNode.content_path = sa.Column("content_path", sa.String)

UserProgress.id = sa.Column("id", sa.BigInteger, primary_key=True)
UserProgress.user_id = sa.Column("user_id", sa.UUID)
UserProgress.node_id = sa.Column("node_id", sa.String)
UserProgress.status = sa.Column("status", sa.String)
UserProgress.confidence_score = sa.Column("confidence_score", sa.Integer)

WeakArea.id = sa.Column("id", sa.BigInteger, primary_key=True)
WeakArea.user_id = sa.Column("user_id", sa.UUID)
WeakArea.node_id = sa.Column("node_id", sa.String)
WeakArea.failure_count = sa.Column("failure_count", sa.Integer)
WeakArea.review_status = sa.Column("review_status", sa.String)


# =============================================================================
# Helper: Seed/Retrieve Test User
# =============================================================================
TEST_USER_UUID = UUID("00000000-0000-0000-0000-000000000000")

async def get_or_create_test_user(db: AsyncSession) -> UUID:
    stmt = select(User).limit(1)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user:
        return user.id

    logger.info("No users found. Seeding default test user...")
    default_user = User(
        id=TEST_USER_UUID,
        email="test_student@aimos.dev",
        password_hash="pbkdf2:sha256:mock_hash_for_dev",
        target_role="Java Developer (Zoho)",
        operating_system="Windows"
    )
    db.add(default_user)
    await db.commit()
    return TEST_USER_UUID


# =============================================================================
# Async Query Selectors
# =============================================================================

async def get_user_node_progress(db: AsyncSession, user_id: UUID, node_id: str) -> Optional[UserProgress]:
    stmt = select(UserProgress).where(
        UserProgress.user_id == user_id,
        UserProgress.node_id == node_id
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_node_weakness(db: AsyncSession, user_id: UUID, node_id: str) -> Optional[WeakArea]:
    stmt = select(WeakArea).where(
        WeakArea.user_id == user_id,
        WeakArea.node_id == node_id,
        WeakArea.review_status == "active"
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_active_weak_areas(db: AsyncSession, user_id: UUID) -> List[WeakArea]:
    stmt = select(WeakArea).where(
        WeakArea.user_id == user_id,
        WeakArea.review_status == "active"
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_curriculum_node(db: AsyncSession, node_id: str) -> Optional[CurriculumNode]:
    stmt = select(CurriculumNode).where(CurriculumNode.id == node_id)
    result = await db.execute(stmt)
    return result.scalars().first()


# =============================================================================
# Async Database Mutation Helpers (Phase 4)
# =============================================================================

async def upsert_user_progress(
    db: AsyncSession,
    user_id: UUID,
    node_id: str,
    status: str,
    confidence_score: int
) -> UserProgress:
    """
    Inserts a user_progress record or updates it if one already exists
    for the given user_id / node_id combination.
    """
    existing = await get_user_node_progress(db, user_id, node_id)
    if existing:
        existing.status = status
        existing.confidence_score = confidence_score
        logger.info("Updated progress for user %s on node %s to %s", user_id, node_id, status)
        return existing
    else:
        new_progress = UserProgress(
            user_id=user_id,
            node_id=node_id,
            status=status,
            confidence_score=confidence_score
        )
        db.add(new_progress)
        logger.info("Created progress for user %s on node %s to %s", user_id, node_id, status)
        return new_progress


async def record_validation_failure(db: AsyncSession, user_id: UUID, node_id: str) -> WeakArea:
    """
    Increments failure count of an active weakness record for the user/node.
    If no weakness record exists, inserts a new one with failure_count = 1.
    """
    existing = await get_node_weakness(db, user_id, node_id)
    if existing:
        existing.failure_count += 1
        logger.info("Incremented failure_count for user %s on node %s to %d", user_id, node_id, existing.failure_count)
        return existing
    else:
        new_weakness = WeakArea(
            user_id=user_id,
            node_id=node_id,
            failure_count=1,
            review_status="active"
        )
        db.add(new_weakness)
        logger.info("Created active weakness for user %s on node %s", user_id, node_id)
        return new_weakness


async def resolve_weakness_record(db: AsyncSession, user_id: UUID, node_id: str) -> None:
    """
    Marks an active weakness record as 'resolved'. Does nothing if no active weakness exists.
    """
    stmt = (
        update(WeakArea)
        .where(
            WeakArea.user_id == user_id,
            WeakArea.node_id == node_id,
            WeakArea.review_status == "active"
        )
        .values(review_status="resolved")
    )
    await db.execute(stmt)
    logger.info("Resolved active weaknesses for user %s on node %s", user_id, node_id)


async def unlock_next_nodes(db: AsyncSession, user_id: UUID, completed_node_id: str) -> List[UserProgress]:
    """
    Identifies all curriculum nodes that have completed_node_id as their prerequisite_id.
    Inserts/updates their status in user_progress to 'unlocked'.
    """
    # 1. Query child nodes
    stmt = select(CurriculumNode).where(CurriculumNode.prerequisite_id == completed_node_id)
    result = await db.execute(stmt)
    child_nodes = result.scalars().all()

    unlocked_records = []
    # 2. Upsert status to unlocked for each child
    for node in child_nodes:
        # Check if already completed/unlocked to avoid resetting status back to unlocked
        existing = await get_user_node_progress(db, user_id, node.id)
        if existing and existing.status in ("completed", "in_progress"):
            continue
        
        rec = await upsert_user_progress(db, user_id, node.id, "unlocked", 0)
        unlocked_records.append(rec)
        
    return unlocked_records
