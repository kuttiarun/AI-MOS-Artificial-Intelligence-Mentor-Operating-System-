"""
AI-MOS — Migration 001: Initial Database Schema
================================================
Revision ID : 001
Revises     : (none — first migration)
Created     : 2026-07-19

Executes the full production DDL defined in Docs/Database.md:

Tables created:
  - users             : Core user accounts & onboarding preferences
  - curriculum_nodes  : Static curriculum knowledge graph (slugged nodes)
  - user_progress     : Per-user curriculum state tracker (locked → completed)
  - weak_areas        : Recurring failure flags for the Memory Engine (MOD-02)

Additional objects:
  - uuid-ossp extension
  - update_modified_column() trigger function (reusable auto-updated_at)
  - 3 triggers: users, user_progress, weak_areas
  - 3 performance indexes optimized for gateway query patterns
  - Initial curriculum_nodes seed data (Phase 1 baseline)

Rollback:
  - Drops all indexes, triggers, tables, and the trigger function in reverse order.
  - Does NOT drop the uuid-ossp extension (may be shared by other tools).
"""

from alembic import op
import sqlalchemy as sa

# ---------------------------------------------------------------------------
# Alembic revision identifiers
# ---------------------------------------------------------------------------
revision: str = "001"
down_revision: str | None = None   # First migration — no parent
branch_labels: str | None = None
depends_on: str | None = None


# ===========================================================================
# UPGRADE — Apply Schema
# ===========================================================================
def upgrade() -> None:
    # -----------------------------------------------------------------------
    # 0. Extensions & Shared Trigger Function
    # -----------------------------------------------------------------------
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_modified_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # -----------------------------------------------------------------------
    # 1. Table: users
    #    Stores user authentication details and onboarding diagnostic config.
    # -----------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE users (
            id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            email            VARCHAR(255) NOT NULL UNIQUE,
            password_hash    VARCHAR(255) NOT NULL,
            target_role      VARCHAR(100) DEFAULT 'Generalist',
            operating_system VARCHAR(50)  NOT NULL,
            created_at       TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at       TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    op.execute(
        """
        CREATE TRIGGER update_users_modtime
            BEFORE UPDATE ON users
            FOR EACH ROW
            EXECUTE FUNCTION update_modified_column();
        """
    )

    # -----------------------------------------------------------------------
    # 2. Table: curriculum_nodes
    #    Represents the static learning tree structure. Prerequisites use
    #    ON DELETE RESTRICT to prevent orphaned dependency chains.
    # -----------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE curriculum_nodes (
            id              VARCHAR(100) PRIMARY KEY,
            title           VARCHAR(255) NOT NULL,
            phase           INT          NOT NULL,
            prerequisite_id VARCHAR(100),
            content_path    VARCHAR(512) NOT NULL,
            created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_prerequisite
                FOREIGN KEY (prerequisite_id)
                REFERENCES curriculum_nodes(id)
                ON DELETE RESTRICT
        );
        """
    )

    # -----------------------------------------------------------------------
    # 3. Table: user_progress
    #    Tracks each user's active state through the curriculum graph.
    #    ON DELETE CASCADE: removing a user cleans up all their progress rows.
    # -----------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE user_progress (
            id               BIGSERIAL PRIMARY KEY,
            user_id          UUID         NOT NULL,
            node_id          VARCHAR(100) NOT NULL,
            status           VARCHAR(50)  NOT NULL DEFAULT 'locked',
            confidence_score INT                   DEFAULT 0,
            created_at       TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at       TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_progress_user
                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            CONSTRAINT fk_progress_node
                FOREIGN KEY (node_id)
                REFERENCES curriculum_nodes(id)
                ON DELETE CASCADE,

            CONSTRAINT check_status
                CHECK (status IN ('locked', 'unlocked', 'in_progress', 'completed')),

            CONSTRAINT check_confidence
                CHECK (confidence_score BETWEEN 0 AND 10),

            CONSTRAINT unique_user_node
                UNIQUE (user_id, node_id)
        );
        """
    )

    op.execute(
        """
        CREATE TRIGGER update_user_progress_modtime
            BEFORE UPDATE ON user_progress
            FOR EACH ROW
            EXECUTE FUNCTION update_modified_column();
        """
    )

    # -----------------------------------------------------------------------
    # 4. Table: weak_areas
    #    Tracks recurring weak items flagged by the AI evaluator (MOD-02).
    #    ON DELETE CASCADE: removing a user cleans up all their weak flags.
    # -----------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE weak_areas (
            id             BIGSERIAL PRIMARY KEY,
            user_id        UUID         NOT NULL,
            node_id        VARCHAR(100) NOT NULL,
            failure_count  INT          NOT NULL DEFAULT 1,
            review_status  VARCHAR(50)  NOT NULL DEFAULT 'active',
            created_at     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at     TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_weak_user
                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            CONSTRAINT fk_weak_node
                FOREIGN KEY (node_id)
                REFERENCES curriculum_nodes(id)
                ON DELETE CASCADE,

            CONSTRAINT check_review_status
                CHECK (review_status IN ('active', 'resolved')),

            CONSTRAINT unique_user_weak_node
                UNIQUE (user_id, node_id)
        );
        """
    )

    op.execute(
        """
        CREATE TRIGGER update_weak_areas_modtime
            BEFORE UPDATE ON weak_areas
            FOR EACH ROW
            EXECUTE FUNCTION update_modified_column();
        """
    )

    # -----------------------------------------------------------------------
    # 5. Performance Indexes (Database.md §3)
    #    Optimized for gateway query patterns described in SRS §1 data flow.
    # -----------------------------------------------------------------------

    # Optimizes user login and session verification queries
    op.execute(
        "CREATE INDEX idx_users_email ON users(email);"
    )

    # Optimizes core engine lookups: "what is this user currently working on?"
    op.execute(
        "CREATE INDEX idx_user_progress_lookup ON user_progress(user_id, status);"
    )

    # Optimizes Research Coach scans: "what are this user's unresolved weaknesses?"
    op.execute(
        "CREATE INDEX idx_weak_areas_active ON weak_areas(user_id, review_status);"
    )

    # -----------------------------------------------------------------------
    # 6. Seed Data — Initial Curriculum Nodes (Phase 1 Baseline)
    #    Establishes the foundational Java learning tree.
    #    Phase 2 will expand this with the full curriculum graph.
    # -----------------------------------------------------------------------
    op.execute(
        """
        INSERT INTO curriculum_nodes (id, title, phase, prerequisite_id, content_path) VALUES
        -- Phase 1: Foundations
        ('foundations-intro',
         'Introduction to Software Engineering',
         1, NULL,
         'curriculum/phase-1/01-intro.md'),

        ('foundations-how-computers-work',
         'How Computers Work: CPU, RAM, Storage',
         1, 'foundations-intro',
         'curriculum/phase-1/02-how-computers-work.md'),

        ('foundations-programming-basics',
         'What is Programming? Variables, Types & Logic',
         1, 'foundations-how-computers-work',
         'curriculum/phase-1/03-programming-basics.md'),

        -- Phase 2: Java Core
        ('java-core-setup',
         'Java Environment Setup: JDK, JVM, JRE',
         2, 'foundations-programming-basics',
         'curriculum/phase-2/01-java-setup.md'),

        ('java-core-oop-classes',
         'Object-Oriented Programming: Classes & Objects',
         2, 'java-core-setup',
         'curriculum/phase-2/02-oop-classes.md'),

        ('java-core-oop-inheritance',
         'OOP: Inheritance & the IS-A Relationship',
         2, 'java-core-oop-classes',
         'curriculum/phase-2/03-oop-inheritance.md'),

        ('java-core-interface',
         'Interfaces: Contracts & Polymorphism',
         2, 'java-core-oop-inheritance',
         'curriculum/phase-2/04-interfaces.md'),

        ('java-core-abstract-class',
         'Abstract Classes: Partial Abstraction Patterns',
         2, 'java-core-interface',
         'curriculum/phase-2/05-abstract-classes.md'),

        -- Phase 3: Java Collections
        ('java-collections-arrays',
         'Arrays: Fixed-Size Contiguous Memory',
         3, 'java-core-abstract-class',
         'curriculum/phase-3/01-arrays.md'),

        ('java-collections-arraylist',
         'ArrayList: Dynamic Array Internals',
         3, 'java-collections-arrays',
         'curriculum/phase-3/02-arraylist.md'),

        ('java-collections-linkedlist',
         'LinkedList: Node-Pointer Architecture',
         3, 'java-collections-arraylist',
         'curriculum/phase-3/03-linkedlist.md'),

        ('java-collections-hashmap',
         'HashMap: Hashing, Buckets & Collision Resolution',
         3, 'java-collections-linkedlist',
         'curriculum/phase-3/04-hashmap.md');
        """
    )


# ===========================================================================
# DOWNGRADE — Reverse Schema (full rollback)
# ===========================================================================
def downgrade() -> None:
    # -----------------------------------------------------------------------
    # Drop in reverse dependency order
    # -----------------------------------------------------------------------

    # Indexes
    op.execute("DROP INDEX IF EXISTS idx_weak_areas_active;")
    op.execute("DROP INDEX IF EXISTS idx_user_progress_lookup;")
    op.execute("DROP INDEX IF EXISTS idx_users_email;")

    # Triggers
    op.execute("DROP TRIGGER IF EXISTS update_weak_areas_modtime ON weak_areas;")
    op.execute("DROP TRIGGER IF EXISTS update_user_progress_modtime ON user_progress;")
    op.execute("DROP TRIGGER IF EXISTS update_users_modtime ON users;")

    # Tables (must drop leaf tables before parent tables due to FK constraints)
    op.execute("DROP TABLE IF EXISTS weak_areas;")
    op.execute("DROP TABLE IF EXISTS user_progress;")
    op.execute("DROP TABLE IF EXISTS curriculum_nodes;")
    op.execute("DROP TABLE IF EXISTS users;")

    # Shared trigger function
    op.execute("DROP FUNCTION IF EXISTS update_modified_column();")

    # NOTE: We intentionally do NOT drop the uuid-ossp extension here,
    # as it may be used by other schemas in the same PostgreSQL instance.
