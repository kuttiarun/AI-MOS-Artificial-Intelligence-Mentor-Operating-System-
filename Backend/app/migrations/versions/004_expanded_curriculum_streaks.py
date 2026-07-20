"""
AI-MOS — Migration 004: Expanded Curriculum + User Streaks
===========================================================
Revision ID : 004
Revises     : 003
Created     : 2026-07-20

Changes:
  - Creates user_streaks table (current_streak, longest_streak, last_active_date)
  - Seeds 17 new curriculum nodes across phases 4 (Java Advanced),
    5 (Software Testing), and 6 (Backend/Spring Boot)
  - Adds prerequisite chains linking phases together

Rollback:
  - Removes all phase 4/5/6 seeded rows from curriculum_nodes
  - Drops user_streaks table
"""

from alembic import op
import sqlalchemy as sa

# ---------------------------------------------------------------------------
# Alembic revision identifiers
# ---------------------------------------------------------------------------
revision: str = "004"
down_revision: str | None = "003"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # 1. Create user_streaks table
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS user_streaks (
            user_id         UUID PRIMARY KEY,
            current_streak  INTEGER NOT NULL DEFAULT 0,
            longest_streak  INTEGER NOT NULL DEFAULT 0,
            last_active_date DATE
        );
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_streaks_user_id
        ON user_streaks (user_id);
    """)

    # -----------------------------------------------------------------------
    # 2. Seed Phase 4 — Java Advanced (6 nodes)
    # -----------------------------------------------------------------------
    op.execute("""
        INSERT INTO curriculum_nodes (id, title, phase, prerequisite_id, content_path)
        VALUES
          ('java-advanced-exceptions',
           'Exception Handling & Error Hierarchy',
           4,
           'java-collections-hashmap',
           'curriculum/phase-4/01-exceptions.md'),
          ('java-advanced-generics',
           'Generics & Bounded Wildcards',
           4,
           'java-advanced-exceptions',
           'curriculum/phase-4/02-generics.md'),
          ('java-advanced-streams',
           'Streams API & Functional Pipelines',
           4,
           'java-advanced-generics',
           'curriculum/phase-4/03-streams-api.md'),
          ('java-advanced-lambda',
           'Lambda Expressions & Functional Interfaces',
           4,
           'java-advanced-streams',
           'curriculum/phase-4/04-lambda-functional.md'),
          ('java-advanced-concurrency',
           'Concurrency — Threads & Synchronization',
           4,
           'java-advanced-lambda',
           'curriculum/phase-4/05-concurrency.md'),
          ('java-advanced-jvm-memory',
           'JVM Memory Model & Garbage Collection',
           4,
           'java-advanced-concurrency',
           'curriculum/phase-4/06-jvm-memory.md')
        ON CONFLICT (id) DO NOTHING;
    """)

    # -----------------------------------------------------------------------
    # 3. Seed Phase 5 — Software Testing (5 nodes)
    # -----------------------------------------------------------------------
    op.execute("""
        INSERT INTO curriculum_nodes (id, title, phase, prerequisite_id, content_path)
        VALUES
          ('testing-junit5',
           'JUnit 5 — Unit Testing Fundamentals',
           5,
           'java-advanced-jvm-memory',
           'curriculum/phase-5/01-unit-testing-junit.md'),
          ('testing-mockito',
           'Mockito — Mocking External Dependencies',
           5,
           'testing-junit5',
           'curriculum/phase-5/02-mockito.md'),
          ('testing-integration',
           'Integration Testing with Spring Boot',
           5,
           'testing-mockito',
           'curriculum/phase-5/03-integration-testing.md'),
          ('testing-tdd',
           'TDD — Red-Green-Refactor Cycle',
           5,
           'testing-integration',
           'curriculum/phase-5/04-tdd-cycle.md'),
          ('testing-coverage',
           'Test Coverage & JaCoCo',
           5,
           'testing-tdd',
           'curriculum/phase-5/05-test-coverage.md')
        ON CONFLICT (id) DO NOTHING;
    """)

    # -----------------------------------------------------------------------
    # 4. Seed Phase 6 — Backend / Spring Boot (6 nodes)
    # -----------------------------------------------------------------------
    op.execute("""
        INSERT INTO curriculum_nodes (id, title, phase, prerequisite_id, content_path)
        VALUES
          ('spring-intro',
           'Spring Boot — IoC, DI & ApplicationContext',
           6,
           'testing-coverage',
           'curriculum/phase-6/01-spring-intro.md'),
          ('spring-mvc',
           'Spring MVC — Building REST APIs',
           6,
           'spring-intro',
           'curriculum/phase-6/02-spring-mvc.md'),
          ('spring-data-jpa',
           'Spring Data JPA & Repository Pattern',
           6,
           'spring-mvc',
           'curriculum/phase-6/03-spring-data-jpa.md'),
          ('spring-rest-design',
           'REST API Design Best Practices',
           6,
           'spring-data-jpa',
           'curriculum/phase-6/04-rest-api-design.md'),
          ('spring-security',
           'Spring Security — JWT Authentication',
           6,
           'spring-rest-design',
           'curriculum/phase-6/05-spring-security.md'),
          ('spring-deployment',
           'Deployment — Docker & CI/CD Pipeline',
           6,
           'spring-security',
           'curriculum/phase-6/06-deployment.md')
        ON CONFLICT (id) DO NOTHING;
    """)


def downgrade() -> None:
    # Remove all phase 4/5/6 nodes
    op.execute("""
        DELETE FROM curriculum_nodes WHERE phase IN (4, 5, 6);
    """)
    # Drop user_streaks
    op.execute("DROP INDEX IF EXISTS idx_user_streaks_user_id;")
    op.execute("DROP TABLE IF EXISTS user_streaks;")
