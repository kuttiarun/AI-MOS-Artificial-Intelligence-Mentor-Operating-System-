"""
AI-MOS Backend — Progress and Weakness Database Selectors & Mutations
=======================================================================
Contains SQLAlchemy 2.0 ORM models and asynchronous database query
and update operations.
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
# ORM Models (Declared correctly inside class bodies)
# =============================================================================

class User(Base):
    __tablename__ = "users"
    id = sa.Column("id", sa.UUID, primary_key=True)
    email = sa.Column("email", sa.String, nullable=False, unique=True)
    password_hash = sa.Column("password_hash", sa.String, nullable=False)
    target_role = sa.Column("target_role", sa.String)
    operating_system = sa.Column("operating_system", sa.String, nullable=False)
    onboarding_complete = sa.Column("onboarding_complete", sa.Boolean, nullable=False, default=False)


class CurriculumNode(Base):
    __tablename__ = "curriculum_nodes"
    id = sa.Column("id", sa.String, primary_key=True)
    title = sa.Column("title", sa.String, nullable=False)
    phase = sa.Column("phase", sa.Integer, nullable=False)
    prerequisite_id = sa.Column("prerequisite_id", sa.String, nullable=True)
    content_path = sa.Column("content_path", sa.String, nullable=False)


class UserProgress(Base):
    __tablename__ = "user_progress"
    id = sa.Column("id", sa.BigInteger, primary_key=True)
    user_id = sa.Column("user_id", sa.UUID, nullable=False)
    node_id = sa.Column("node_id", sa.String, nullable=False)
    status = sa.Column("status", sa.String, nullable=False, default="locked")
    confidence_score = sa.Column("confidence_score", sa.Integer, default=0)


class WeakArea(Base):
    __tablename__ = "weak_areas"
    id = sa.Column("id", sa.BigInteger, primary_key=True)
    user_id = sa.Column("user_id", sa.UUID, nullable=False)
    node_id = sa.Column("node_id", sa.String, nullable=False)
    failure_count = sa.Column("failure_count", sa.Integer, nullable=False, default=1)
    review_status = sa.Column("review_status", sa.String, nullable=False, default="active")


class ContentTelemetry(Base):
    __tablename__ = "content_telemetry"
    id = sa.Column("id", sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column("user_id", sa.UUID, nullable=True)
    node_id = sa.Column("node_id", sa.String, nullable=False)
    time_spent_seconds = sa.Column("time_spent_seconds", sa.Float, nullable=False)
    attempts = sa.Column("attempts", sa.Integer, nullable=False)
    passed = sa.Column("passed", sa.Boolean, nullable=False)
    created_at = sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now())


class AnalogyPerformanceAggregate(Base):
    __tablename__ = "analogy_performance_aggregates"
    node_id = sa.Column("node_id", sa.String, primary_key=True)
    total_impressions = sa.Column("total_impressions", sa.Integer, nullable=False, default=0)
    first_pass_velocity = sa.Column("first_pass_velocity", sa.Float, nullable=False, default=0.0)
    average_attempts = sa.Column("average_attempts", sa.Float, nullable=False, default=0.0)
    updated_at = sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now())



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
        operating_system="Windows",
        onboarding_complete=True,  # Test users bypass the onboarding gate
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
# Async Database Mutation Helpers
# =============================================================================

async def upsert_user_progress(
    db: AsyncSession,
    user_id: UUID,
    node_id: str,
    status: str,
    confidence_score: int
) -> UserProgress:
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
    stmt = select(CurriculumNode).where(CurriculumNode.prerequisite_id == completed_node_id)
    result = await db.execute(stmt)
    child_nodes = result.scalars().all()

    unlocked_records = []
    for node in child_nodes:
        existing = await get_user_node_progress(db, user_id, node.id)
        if existing and existing.status in ("completed", "in_progress"):
            continue
        
        rec = await upsert_user_progress(db, user_id, node.id, "unlocked", 0)
        unlocked_records.append(rec)
        
    return unlocked_records
