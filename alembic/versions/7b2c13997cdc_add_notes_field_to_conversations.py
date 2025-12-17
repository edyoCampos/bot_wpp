"""add_notes_field_to_conversations

Revision ID: 7b2c13997cdc
Revises: e39f00a90b1e
Create Date: 2025-12-16 19:48:09.558356

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b2c13997cdc'
down_revision: Union[str, Sequence[str], None] = 'e39f00a90b1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('conversations', sa.Column('notes', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('conversations', 'notes')
