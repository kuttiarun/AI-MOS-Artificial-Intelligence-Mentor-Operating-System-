"""
AI-MOS Backend — Content Analytics & Ingestion Unit/Integration Tests
=====================================================================
Verifies the async telemetry ingestion endpoints and background worker db aggregates calculation.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, delete

from app.main import app
from app.core.database import AsyncSessionLocal
from app.services.progress import (
    User,
    CurriculumNode,
    ContentTelemetry,
    AnalogyPerformanceAggregate,
)
from app.api.v1.endpoints.analytics import update_telemetry_aggregates


@pytest_asyncio.fixture
async def db_setup():
    """Seeds a test user and curriculum nodes if they don't exist yet."""
    async with AsyncSessionLocal() as session:
        # Seed test user
        from uuid import UUID
        user_uuid = UUID("00000000-0000-0000-0000-000000000000")
        user_check = await session.get(User, user_uuid)
        if not user_check:
            test_user = User(
                id=user_uuid,
                email="test_analytics_student@aimos.dev",
                password_hash="pbkdf2:sha256:mock_hash_for_dev",
                target_role="Java Developer (Zoho)",
                operating_system="Windows"
            )
            session.add(test_user)
            await session.commit()

        # Seed node
        node_check = await session.get(CurriculumNode, "java-core-interface")
        if not node_check:
            session.add(
                CurriculumNode(
                    id="java-core-interface",
                    title="Interfaces",
                    phase=2,
                    content_path="curriculum/phase-2/04-interfaces.md"
                )
            )
            await session.commit()

        # Clean up prior telemetry / aggregates
        await session.execute(delete(ContentTelemetry).where(ContentTelemetry.node_id == "java-core-interface"))
        await session.execute(delete(AnalogyPerformanceAggregate).where(AnalogyPerformanceAggregate.node_id == "java-core-interface"))
        await session.commit()

    yield user_uuid
    
    # Dispose of the engine connection pool to prevent connection reuse across different event loops
    from app.core.database import engine
    await engine.dispose()


async def test_telemetry_endpoint_ingestion(db_setup):
    """
    Verifies that the /log endpoint registers requests successfully with 202 Accepted.
    """
    user_id_str = str(db_setup)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/analytics/log",
            headers={
                "X-User-Id": user_id_str
            },
            json={
                "node_id": "java-core-interface",
                "time_spent_seconds": 45.2,
                "attempts": 2,
                "passed": True
            }
        )

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert "queued" in data["message"]


async def test_background_worker_aggregates(db_setup):
    """
    Verifies the telemetry ingestion calculation rules.
    Checks impressions count, first-pass velocity (%), and average validation attempts.
    """
    user_uuid = db_setup
    node_id = "java-core-interface"

    # Make sure DB stats are clean
    async with AsyncSessionLocal() as session:
        await session.execute(delete(ContentTelemetry).where(ContentTelemetry.node_id == node_id))
        await session.execute(delete(AnalogyPerformanceAggregate).where(AnalogyPerformanceAggregate.node_id == node_id))
        await session.commit()

    # 1. First attempt: Passed on first try
    await update_telemetry_aggregates(
        user_uuid=user_uuid,
        node_id=node_id,
        time_spent_seconds=30.0,
        attempts=1,
        passed=True
    )

    async with AsyncSessionLocal() as session:
        # Verify telemetry row created
        tel_stmt = select(ContentTelemetry).where(ContentTelemetry.node_id == node_id)
        telemetries = (await session.execute(tel_stmt)).scalars().all()
        assert len(telemetries) == 1
        assert telemetries[0].time_spent_seconds == 30.0
        assert telemetries[0].attempts == 1
        assert telemetries[0].passed is True

        # Verify aggregates
        agg_stmt = select(AnalogyPerformanceAggregate).where(AnalogyPerformanceAggregate.node_id == node_id)
        agg = (await session.execute(agg_stmt)).scalars().first()
        assert agg is not None
        assert agg.total_impressions == 1
        assert agg.first_pass_velocity == 1.0  # 1/1 passed on first try
        assert agg.average_attempts == 1.0  # 1 attempt average

    # 2. Second attempt: Failed with 3 attempts
    await update_telemetry_aggregates(
        user_uuid=user_uuid,
        node_id=node_id,
        time_spent_seconds=60.0,
        attempts=3,
        passed=False
    )

    async with AsyncSessionLocal() as session:
        tel_stmt = select(ContentTelemetry).where(ContentTelemetry.node_id == node_id)
        telemetries = (await session.execute(tel_stmt)).scalars().all()
        assert len(telemetries) == 2

        # Verify recalculated aggregates
        agg_stmt = select(AnalogyPerformanceAggregate).where(AnalogyPerformanceAggregate.node_id == node_id)
        agg = (await session.execute(agg_stmt)).scalars().first()
        assert agg is not None
        assert agg.total_impressions == 2
        assert agg.first_pass_velocity == 0.5  # 1 out of 2 passed on first try
        assert agg.average_attempts == 2.0  # average of 1 and 3 is 2
