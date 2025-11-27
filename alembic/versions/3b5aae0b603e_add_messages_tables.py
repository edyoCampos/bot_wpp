"""add messages tables

Revision ID: 3b5aae0b603e
Revises: 2858bd6fb0d6
Create Date: 2025-11-18 10:04:00.109346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '3b5aae0b603e'
down_revision: Union[str, Sequence[str], None] = '2858bd6fb0d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('type', sa.String(50), nullable=False, index=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "type IN ('text', 'image', 'voice', 'video', 'document', 'location')", name='message_type_check'),
    )

    # Create message_media table
    op.create_table(
        'message_media',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('message_id', postgresql.UUID(
            as_uuid=True), nullable=False, index=True),
        sa.Column('mimetype', sa.String(255), nullable=False),
        sa.Column('filename', sa.String(500), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ['message_id'], ['messages.id'], ondelete='CASCADE'),
    )

    # Create message_location table
    op.create_table(
        'message_location',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('message_id', postgresql.UUID(as_uuid=True),
                  nullable=False, unique=True, index=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('title', sa.String(500), nullable=True),
        sa.ForeignKeyConstraint(
            ['message_id'], ['messages.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('message_location')
    op.drop_table('message_media')
    op.drop_table('messages')
