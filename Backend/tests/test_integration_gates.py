"""
AI-MOS Backend — End-to-End Integration Tests
==============================================
Verifies the Socratic validation checkpoint progression, transaction safety
guarantees, and DB state tracking under different evaluator outcomes.
"""

from unittest.mock import patch
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.core.database import AsyncSessionLocal
from app.services.progress import UserProgress, WeakArea, User, CurriculumNode


# Setup fixture to seed nodes and user for tests
@pytest_asyncio.fixture
async def db_session():
    """Provides a database session for test verification."""
    async with AsyncSessionLocal() as session:
        yield session
    
    from app.core.database import engine
    await engine.dispose()


async def test_validation_gate_flow(db_session):
    """
    Integration test verifying progress state changes after passing and failing validation checks.
    """
    # 1. Assert seed user exists (or trigger retrieval helper)
    # This matches the default user id set in progress.py: TEST_USER_UUID
    user_id_str = "00000000-0000-0000-0000-000000000000"

    # Make sure interface and hashmap nodes are seeded in DB
    async with AsyncSessionLocal() as session:
        # Seed test user first by exact UUID to ensure it exists
        from app.services.progress import User
        from uuid import UUID
        user_check = await session.get(User, UUID("00000000-0000-0000-0000-000000000000"))
        if not user_check:
            test_user = User(
                id=UUID("00000000-0000-0000-0000-000000000000"),
                email="test_student@aimos.dev",
                password_hash="pbkdf2:sha256:mock_hash_for_dev",
                target_role="Java Developer (Zoho)",
                operating_system="Windows"
            )
            session.add(test_user)
            await session.commit()

        # Clean up any leftover progress or weakness records from previous test runs
        import sqlalchemy as sa
        from app.services.progress import UserProgress, WeakArea
        await session.execute(sa.delete(UserProgress).where(UserProgress.user_id == UUID("00000000-0000-0000-0000-000000000000")))
        await session.execute(sa.delete(WeakArea).where(WeakArea.user_id == UUID("00000000-0000-0000-0000-000000000000")))
        await session.commit()

        # Check if node java-core-interface exists
        node_check = await session.execute(select(CurriculumNode).where(CurriculumNode.id == "java-core-interface"))
        if not node_check.scalars().first():
            # Seed nodes if not present (helps if ran without alembic migration first)
            session.add(CurriculumNode(id="java-core-interface", title="Interfaces", phase=2, content_path="curriculum/phase-2/04-interfaces.md"))
            session.add(CurriculumNode(id="java-collections-hashmap", title="HashMap", phase=3, prerequisite_id="java-core-interface", content_path="curriculum/phase-3/04-hashmap.md"))
            await session.commit()

    # -------------------------------------------------------------------------
    # Scenario A: Fail validation check
    # -------------------------------------------------------------------------
    mock_fail = {
        "passed": False,
        "confidence_score": 3,
        "feedback": "Your explanation does not explain interface polymorphism. Try again."
    }

    # Patch the Socratic evaluator to return mock_fail
    with patch("app.services.evaluator.SocraticEvaluator.evaluate_explanation", return_value=mock_fail):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/curriculum/validate",
                headers={
                    "X-User-API-Key": "mock-api-key",
                    "X-User-Provider": "nvidia-nim",
                    "X-User-Id": user_id_str
                },
                json={
                    "node_id": "java-core-interface",
                    "submission_type": "explanation",
                    "user_text": "An interface is just a code block."
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data["passed"] is False
        assert data["confidence_score"] == 3
        assert data["next_node_id"] is None

        # Verify DB updates: user_progress should be in_progress and weak_areas failures should be 1
        async with AsyncSessionLocal() as session:
            progress_stmt = select(UserProgress).where(
                UserProgress.user_id == user_id_str,
                UserProgress.node_id == "java-core-interface"
            )
            prog_res = await session.execute(progress_stmt)
            prog = prog_res.scalars().first()
            assert prog is not None
            assert prog.status == "in_progress"
            assert prog.confidence_score == 3

            weakness_stmt = select(WeakArea).where(
                WeakArea.user_id == user_id_str,
                WeakArea.node_id == "java-core-interface",
                WeakArea.review_status == "active"
            )
            weak_res = await session.execute(weakness_stmt)
            weak = weak_res.scalars().first()
            assert weak is not None
            assert weak.failure_count == 1

    # -------------------------------------------------------------------------
    # Scenario B: Fail again to verify failure count increments
    # -------------------------------------------------------------------------
    with patch("app.services.evaluator.SocraticEvaluator.evaluate_explanation", return_value=mock_fail):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/curriculum/validate",
                headers={
                    "X-User-API-Key": "mock-api-key",
                    "X-User-Provider": "nvidia-nim",
                    "X-User-Id": user_id_str
                },
                json={
                    "node_id": "java-core-interface",
                    "submission_type": "explanation",
                    "user_text": "An interface is still just a code block."
                }
            )
        assert response.status_code == 200

        # Verify failure count is now 2
        async with AsyncSessionLocal() as session:
            weak_res = await session.execute(weakness_stmt)
            weak = weak_res.scalars().first()
            assert weak is not None
            assert weak.failure_count == 2

    # -------------------------------------------------------------------------
    # Scenario C: Pass validation check
    # -------------------------------------------------------------------------
    mock_pass = {
        "passed": True,
        "confidence_score": 9,
        "feedback": "Perfect description of dynamic polymorphism contracts!"
    }

    with patch("app.services.evaluator.SocraticEvaluator.evaluate_explanation", return_value=mock_pass):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/curriculum/validate",
                headers={
                    "X-User-API-Key": "mock-api-key",
                    "X-User-Provider": "nvidia-nim",
                    "X-User-Id": user_id_str
                },
                json={
                    "node_id": "java-core-interface",
                    "submission_type": "explanation",
                    "user_text": "An interface is a completely abstract type used to specify a contract that subclasses must implement."
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data["passed"] is True
        assert data["confidence_score"] == 9
        # The unlocked child node should be returned
        assert data["next_node_id"] in ("java-collections-hashmap", "java-core-abstract-class")

        # Verify DB updates: user_progress is completed, weakness is resolved, child is unlocked
        async with AsyncSessionLocal() as session:
            prog_res = await session.execute(progress_stmt)
            prog = prog_res.scalars().first()
            assert prog is not None
            assert prog.status == "completed"
            assert prog.confidence_score == 9

            # Child node should be unlocked
            child_stmt = select(UserProgress).where(
                UserProgress.user_id == user_id_str,
                UserProgress.node_id.in_(["java-collections-hashmap", "java-core-abstract-class"])
            )
            child_res = await session.execute(child_stmt)
            child = child_res.scalars().first()
            assert child is not None
            assert child.status == "unlocked"

            # Check that weakness has been resolved (status resolved or no active ones)
            active_weak_res = await session.execute(weakness_stmt)
            active_weak = active_weak_res.scalars().first()
            assert active_weak is None  # resolved should filter out active status
