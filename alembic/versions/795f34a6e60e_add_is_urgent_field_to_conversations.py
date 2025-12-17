"""add_is_urgent_field_to_conversations

Revision ID: 795f34a6e60e
Revises: 0ad80de67a9f
Create Date: 2025-12-16 19:41:21.085550

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '795f34a6e60e'
down_revision: Union[str, Sequence[str], None] = '0ad80de67a9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('conversations', sa.Column('is_urgent', sa.Boolean(), nullable=False, server_default='false'))
    op.create_index(op.f('ix_conversations_is_urgent'), 'conversations', ['is_urgent'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_conversations_is_urgent'), table_name='conversations')
    op.drop_column('conversations', 'is_urgent')
