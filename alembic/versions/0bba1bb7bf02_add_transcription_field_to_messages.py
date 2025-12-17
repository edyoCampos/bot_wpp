"""add_transcription_field_to_messages

Revision ID: 0bba1bb7bf02
Revises: 1d16df8031e5
Create Date: 2025-12-17 17:00:55.839492

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0bba1bb7bf02'
down_revision: Union[str, Sequence[str], None] = '1d16df8031e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add transcription field to messages table for audio content."""
    op.add_column(
        'messages',
        sa.Column('transcription', sa.Text, nullable=True)
    )
    op.add_column(
        'messages',
        sa.Column('audio_url', sa.String(500), nullable=True)
    )
    op.add_column(
        'messages',
        sa.Column('has_audio', sa.Boolean, default=False, nullable=False, server_default='false')
    )


def downgrade() -> None:
    """Remove transcription field from messages table."""
    op.drop_column('messages', 'has_audio')
    op.drop_column('messages', 'audio_url')
    op.drop_column('messages', 'transcription')
