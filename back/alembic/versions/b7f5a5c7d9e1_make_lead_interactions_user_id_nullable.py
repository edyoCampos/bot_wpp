"""Make lead_interactions.user_id nullable

Revision ID: b7f5a5c7d9e1
Revises: c2f1d8a4b7c9
Create Date: 2026-02-02 19:10:00.000000
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7f5a5c7d9e1"
down_revision: str | None = "c2f1d8a4b7c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Allow NULL user_id for bot interactions."""
    op.alter_column(
        "lead_interactions",
        "user_id",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    """Revert user_id to NOT NULL."""
    op.execute("DELETE FROM lead_interactions WHERE user_id IS NULL")
    op.alter_column(
        "lead_interactions",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
