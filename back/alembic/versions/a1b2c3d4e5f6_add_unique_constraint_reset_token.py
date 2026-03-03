"""add_unique_constraint_reset_token

Revision ID: a1b2c3d4e5f6
Revises: e75f64ab040b
Create Date: 2026-01-15 11:25:02

Adds unique constraint to credentials.reset_token to prevent duplicate tokens.
This is a critical security fix to ensure password reset tokens are unique.
"""

# pylint: disable=no-member,invalid-name,line-too-long
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "e75f64ab040b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add unique constraint to reset_token column."""
    # Create unique constraint on reset_token
    # Note: This will fail if there are duplicate reset_tokens in production
    # Run data cleanup before applying this migration if needed
    op.create_unique_constraint("uq_credentials_reset_token", "credentials", ["reset_token"])


def downgrade() -> None:
    """Remove unique constraint from reset_token column."""
    op.drop_constraint("uq_credentials_reset_token", "credentials", type_="unique")
