"""
AI-MOS — Migration 002: Add Onboarding Completion Flag
=======================================================
Revision ID : 002
Revises     : 001
Created     : 2026-07-20

Adds a boolean column `onboarding_complete` to the `users` table
to gate the main dashboard behind the Module 01 diagnostic flow.

Default FALSE ensures all existing users pass through the onboarding
check on their next session (or can be manually seeded to TRUE for
test/dev users via the test fixture).
"""

from alembic import op
import sqlalchemy as sa

# ---------------------------------------------------------------------------
# Alembic revision identifiers
# ---------------------------------------------------------------------------
revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | None = None
depends_on: str | None = None


# ===========================================================================
# UPGRADE — Add onboarding_complete column
# ===========================================================================
def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE users
          ADD COLUMN IF NOT EXISTS onboarding_complete BOOLEAN NOT NULL DEFAULT FALSE;
        """
    )


# ===========================================================================
# DOWNGRADE — Remove onboarding_complete column
# ===========================================================================
def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE users DROP COLUMN IF EXISTS onboarding_complete;
        """
    )
