"""add_tags_and_conversation_tags_tables

Revision ID: e39f00a90b1e
Revises: 795f34a6e60e
Create Date: 2025-12-16 19:45:38.622118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e39f00a90b1e'
down_revision: Union[str, Sequence[str], None] = '795f34a6e60e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=True)
    
    # Create conversation_tags association table
    op.create_table(
        'conversation_tags',
        sa.Column('conversation_id', sa.String(length=36), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('conversation_id', 'tag_id')
    )
    op.create_index(op.f('ix_conversation_tags_conversation_id'), 'conversation_tags', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_conversation_tags_tag_id'), 'conversation_tags', ['tag_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_conversation_tags_tag_id'), table_name='conversation_tags')
    op.drop_index(op.f('ix_conversation_tags_conversation_id'), table_name='conversation_tags')
    op.drop_table('conversation_tags')
    op.drop_index(op.f('ix_tags_name'), table_name='tags')
    op.drop_table('tags')
