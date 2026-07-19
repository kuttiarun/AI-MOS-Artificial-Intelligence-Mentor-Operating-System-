"""
AI-MOS Backend — Telemetry & Analytics Endpoints
==================================================
Provides non-blocking ingestion for student interaction metrics and updates 
global concept aggregates asynchronously via background workers.
"""

import logging
from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, get_db
from app.services.progress import (
    get_or_create_test_user,
    get_curriculum_node,
    ContentTelemetry,
    AnalogyPerformanceAggregate,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Request/Response Schemas
# =============================================================================

class TelemetryPayload(BaseModel):
    node_id: str = Field(..., description="The curriculum node ID being exited.")
    time_spent_seconds: float = Field(..., ge=0.0, description="Total seconds spent on the node.")
    attempts: int = Field(..., ge=0, description="Validation attempts during the session.")
    passed: bool = Field(..., description="Whether the user passed the validation checkpoint.")


class TelemetryResponse(BaseModel):
    status: str
    message: str


# =============================================================================
# Background Worker logic
# =============================================================================

async def update_telemetry_aggregates(
    user_uuid: UUID,
    node_id: str,
    time_spent_seconds: float,
    attempts: int,
    passed: bool,
) -> None:
    """
    Background worker: writes raw telemetry to the database and recalculates
    global analytics aggregates for the given node without blocking the API call.
    """
    logger.info("Processing background telemetry update for node '%s' (user: %s)", node_id, user_uuid)

    async with AsyncSessionLocal() as db:
        try:
            # 1. Verify node exists to prevent foreign key errors
            node = await get_curriculum_node(db, node_id)
            if not node:
                logger.warning("Node ID '%s' not found in curriculum_nodes. Discarding telemetry.", node_id)
                return

            # 2. Insert raw telemetry record
            telemetry = ContentTelemetry(
                user_id=user_uuid,
                node_id=node_id,
                time_spent_seconds=time_spent_seconds,
                attempts=attempts,
                passed=passed,
            )
            db.add(telemetry)
            await db.flush()  # Ensures telemetry is persisted before we query aggregates

            # 3. Recalculate aggregates for this node
            # Fetch total impressions
            impressions_stmt = select(func.count(ContentTelemetry.id)).where(ContentTelemetry.node_id == node_id)
            impressions_res = await db.execute(impressions_stmt)
            total_impressions = impressions_res.scalar() or 0

            # Fetch first-pass successful attempts (passed on first try, attempts == 1 and passed == True)
            first_pass_stmt = select(func.count(ContentTelemetry.id)).where(
                ContentTelemetry.node_id == node_id,
                ContentTelemetry.attempts == 1,
                ContentTelemetry.passed == True,
            )
            first_pass_res = await db.execute(first_pass_stmt)
            first_pass_count = first_pass_res.scalar() or 0

            # Calculate first pass velocity
            first_pass_velocity = (first_pass_count / total_impressions) if total_impressions > 0 else 0.0

            # Fetch average attempts (excluding cases with 0 attempts if they didn't even try validation)
            avg_attempts_stmt = select(func.avg(ContentTelemetry.attempts)).where(
                ContentTelemetry.node_id == node_id,
                ContentTelemetry.attempts > 0,
            )
            avg_attempts_res = await db.execute(avg_attempts_stmt)
            average_attempts = float(avg_attempts_res.scalar() or 0.0)

            # 4. Upsert analogy_performance_aggregates
            agg_stmt = select(AnalogyPerformanceAggregate).where(AnalogyPerformanceAggregate.node_id == node_id)
            agg_res = await db.execute(agg_stmt)
            aggregate = agg_res.scalars().first()

            if aggregate:
                aggregate.total_impressions = total_impressions
                aggregate.first_pass_velocity = first_pass_velocity
                aggregate.average_attempts = average_attempts
                logger.info("Updated aggregates for node '%s': impressions=%d, velocity=%.2f, avg_attempts=%.2f",
                            node_id, total_impressions, first_pass_velocity, average_attempts)
            else:
                aggregate = AnalogyPerformanceAggregate(
                    node_id=node_id,
                    total_impressions=total_impressions,
                    first_pass_velocity=first_pass_velocity,
                    average_attempts=average_attempts,
                )
                db.add(aggregate)
                logger.info("Created aggregate for node '%s': impressions=%d, velocity=%.2f, avg_attempts=%.2f",
                            node_id, total_impressions, first_pass_velocity, average_attempts)

            await db.commit()

        except Exception as exc:
            logger.error("Error updating telemetry aggregates: %s", str(exc))
            await db.rollback()


# =============================================================================
# POST /log
# =============================================================================

@router.post(
    "/log",
    summary="Ingest Client Interaction Telemetry",
    response_model=TelemetryResponse,
    status_code=202,
)
async def log_telemetry(
    request: TelemetryPayload,
    background_tasks: BackgroundTasks,
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    db: AsyncSession = Depends(get_db),
) -> TelemetryResponse:
    """
    Receives user interaction time spent and checkpoint validation attempts.
    Updates telemetry records and aggregates asynchronously in a background worker task.
    Returns instantly with HTTP 202 Accepted.
    """
    # Resolve user identity
    user_uuid = None
    if x_user_id:
        try:
            user_uuid = UUID(x_user_id.strip())
        except ValueError:
            pass

    if not user_uuid:
        user_uuid = await get_or_create_test_user(db)

    # Queue telemetry processing asynchronously to avoid API call latency
    background_tasks.add_task(
        update_telemetry_aggregates,
        user_uuid=user_uuid,
        node_id=request.node_id,
        time_spent_seconds=request.time_spent_seconds,
        attempts=request.attempts,
        passed=request.passed,
    )

    return TelemetryResponse(
        status="accepted",
        message="Interaction telemetry queued for async processing."
    )
