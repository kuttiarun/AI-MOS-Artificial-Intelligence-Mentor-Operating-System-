"""
AI-MOS — Migration 003: Content Telemetry & Performance Aggregates
===================================================================
Revision ID : 003
Revises     : 002
Created     : 2026-07-20

Creates content_telemetry and analogy_performance_aggregates tables to track 
student interaction times and success velocity.
"""

from alembic import op
import sqlalchemy as sa

# ---------------------------------------------------------------------------
# Alembic revision identifiers
# ---------------------------------------------------------------------------
revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | None = None
depends_on: str | None = None


# ===========================================================================
# UPGRADE — Create tables
# ===========================================================================
def upgrade() -> None:
    # 1. Create content_telemetry table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS content_telemetry (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES users(id) ON DELETE SET NULL,
            node_id VARCHAR(100) REFERENCES curriculum_nodes(id) ON DELETE CASCADE,
            time_spent_seconds DOUBLE PRECISION NOT NULL,
            attempts INTEGER NOT NULL,
            passed BOOLEAN NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    # Create indexes for telemetry lookup performance
    op.execute("CREATE INDEX IF NOT EXISTS idx_content_telemetry_node_id ON content_telemetry(node_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_content_telemetry_user_id ON content_telemetry(user_id);")

    # 2. Create analogy_performance_aggregates table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS analogy_performance_aggregates (
            node_id VARCHAR(100) PRIMARY KEY REFERENCES curriculum_nodes(id) ON DELETE CASCADE,
            total_impressions INTEGER NOT NULL DEFAULT 0,
            first_pass_velocity DOUBLE PRECISION NOT NULL DEFAULT 0.0,
            average_attempts DOUBLE PRECISION NOT NULL DEFAULT 0.0,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


# ===========================================================================
# DOWNGRADE — Remove tables
# ===========================================================================
def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS analogy_performance_aggregates;")
    op.execute("DROP INDEX IF EXISTS idx_content_telemetry_user_id;")
    op.execute("DROP INDEX IF EXISTS idx_content_telemetry_node_id;")
    op.execute("DROP TABLE IF EXISTS content_telemetry;")
