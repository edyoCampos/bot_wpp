"""add_notifications_table

Revision ID: 0ad80de67a9f
Revises: 6f4e7d8c9b2a
Create Date: 2025-12-16 19:32:28.409944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ad80de67a9f'
down_revision: Union[str, Sequence[str], None] = '6f4e7d8c9b2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('type', sa.String(50), nullable=False, comment='Tipo: NEW_LEAD, NEW_MESSAGE, etc.'),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('read', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, index=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('notifications')
