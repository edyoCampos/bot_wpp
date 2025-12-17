"""merge_playbook_and_audit_migrations

Revision ID: 1d16df8031e5
Revises: 3104e8d66510, f5a6b8c9d2e1
Create Date: 2025-12-17 15:15:26.636017

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d16df8031e5'
down_revision: Union[str, Sequence[str], None] = ('3104e8d66510', 'f5a6b8c9d2e1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
