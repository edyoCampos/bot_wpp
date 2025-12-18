"""merge_handoff_and_transcription

Revision ID: 007ad6343e57
Revises: 0bba1bb7bf02, 8c3f4d5e6a7b
Create Date: 2025-12-18 02:13:53.570607

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007ad6343e57'
down_revision: Union[str, Sequence[str], None] = ('0bba1bb7bf02', '8c3f4d5e6a7b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
