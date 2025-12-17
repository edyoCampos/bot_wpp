"""add_deleted_at_to_leads

Revision ID: ae88eb979ccb
Revises: 7b2c13997cdc
Create Date: 2025-12-16 19:52:47.543750

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae88eb979ccb'
down_revision: Union[str, Sequence[str], None] = '7b2c13997cdc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('leads', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_leads_deleted_at'), 'leads', ['deleted_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_leads_deleted_at'), table_name='leads')
    op.drop_column('leads', 'deleted_at')
