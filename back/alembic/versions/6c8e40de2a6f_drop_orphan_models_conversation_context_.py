# pylint: disable=no-member,invalid-name,line-too-long
"""drop_orphan_models_conversation_context_and_alert

Revision ID: 6c8e40de2a6f
Revises: a1b2c3d4e5f6
Create Date: 2026-01-05 11:42:12.374225

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6c8e40de2a6f"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Drop orphan tables: conversation_contexts and alerts.

    Justificativa:
    - conversation_contexts: Nunca usado, redundante com ChromaDB vector storage
    - alerts: Substituído por logging estruturado (core.logging_setup)
    """
    # Drop conversation_contexts table
    op.execute("DROP TABLE IF EXISTS conversation_contexts")  # noqa: F405

    # Drop alerts table
    op.execute("DROP TABLE IF EXISTS alerts")  # noqa: F405


def downgrade() -> None:
    """Recreate orphan tables if needed for rollback."""
    # Recreate alerts table
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Recreate conversation_contexts table
    op.create_table(
        "conversation_contexts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("context_summary", sa.Text(), nullable=True),
        sa.Column("last_topics", sa.JSON(), nullable=True),
        sa.Column("intent_history", sa.JSON(), nullable=True),
        sa.Column("lead_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("conversation_id"),
    )
