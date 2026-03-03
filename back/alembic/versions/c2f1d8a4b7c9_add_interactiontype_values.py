# pylint: disable=no-member,invalid-name,line-too-long
"""Add MESSAGE and MEETING to interactiontype enum

Revision ID: c2f1d8a4b7c9
Revises: 9d9796c95ff4
Create Date: 2026-02-01 03:12:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c2f1d8a4b7c9"
down_revision: str | Sequence[str] | None = "9d9796c95ff4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE interactiontype ADD VALUE IF NOT EXISTS 'MESSAGE'")
    op.execute("ALTER TYPE interactiontype ADD VALUE IF NOT EXISTS 'MEETING'")


def downgrade() -> None:
    """Downgrade schema."""
    # Removing enum values is unsafe and not supported here.
    return
