"""add_topics_playbooks_and_enhance_messages

Revision ID: f5a6b8c9d2e1
Revises: e39f00a90b1e
Create Date: 2025-12-17 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5a6b8c9d2e1'
down_revision: Union[str, None] = 'e39f00a90b1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # STEP 1: Enhance messages table with description, title, tags
    # ============================================================
    op.add_column('messages', sa.Column('title', sa.String(255), nullable=True))
    op.add_column('messages', sa.Column('description', sa.Text, nullable=True))
    op.add_column('messages', sa.Column('tags', sa.String(500), nullable=True))
    
    # Add index for better search performance
    op.create_index('ix_messages_tags', 'messages', ['tags'])
    op.create_index('ix_messages_title', 'messages', ['title'])

    # ============================================================
    # STEP 2: Create topics table (generic contexts for playbooks)
    # ============================================================
    op.create_table(
        'topics',
        sa.Column('id', sa.dialects.postgresql.UUID, primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    op.create_index('ix_topics_name', 'topics', ['name'])
    op.create_index('ix_topics_category', 'topics', ['category'])
    op.create_index('ix_topics_active', 'topics', ['active'])

    # ============================================================
    # STEP 3: Create playbooks table (organized message sequences)
    # ============================================================
    op.create_table(
        'playbooks',
        sa.Column('id', sa.dialects.postgresql.UUID, primary_key=True),
        sa.Column('topic_id', sa.dialects.postgresql.UUID, sa.ForeignKey('topics.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    op.create_index('ix_playbooks_topic_id', 'playbooks', ['topic_id'])
    op.create_index('ix_playbooks_name', 'playbooks', ['name'])
    op.create_index('ix_playbooks_active', 'playbooks', ['active'])

    # ============================================================
    # STEP 4: Create playbook_steps table (ordered message sequence)
    # ============================================================
    op.create_table(
        'playbook_steps',
        sa.Column('id', sa.dialects.postgresql.UUID, primary_key=True),
        sa.Column('playbook_id', sa.dialects.postgresql.UUID, sa.ForeignKey('playbooks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('message_id', sa.dialects.postgresql.UUID, sa.ForeignKey('messages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('step_order', sa.Integer, nullable=False),
        sa.Column('context_hint', sa.Text, nullable=True),  # When to use this step
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    op.create_index('ix_playbook_steps_playbook_id', 'playbook_steps', ['playbook_id'])
    op.create_index('ix_playbook_steps_message_id', 'playbook_steps', ['message_id'])
    op.create_index('ix_playbook_steps_order', 'playbook_steps', ['playbook_id', 'step_order'])
    
    # Unique constraint: each playbook can't have duplicate step_order
    op.create_unique_constraint('uq_playbook_steps_playbook_order', 'playbook_steps', ['playbook_id', 'step_order'])

    # ============================================================
    # STEP 5: Create playbook_embeddings table (for RAG search)
    # ============================================================
    op.create_table(
        'playbook_embeddings',
        sa.Column('id', sa.dialects.postgresql.UUID, primary_key=True),
        sa.Column('playbook_id', sa.dialects.postgresql.UUID, sa.ForeignKey('playbooks.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('embedding_text', sa.Text, nullable=False),  # Combined text for embedding
        sa.Column('chroma_doc_id', sa.String(255), nullable=True, unique=True),  # ChromaDB document ID
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    op.create_index('ix_playbook_embeddings_playbook_id', 'playbook_embeddings', ['playbook_id'])
    op.create_index('ix_playbook_embeddings_chroma_doc_id', 'playbook_embeddings', ['chroma_doc_id'])


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('playbook_embeddings')
    op.drop_table('playbook_steps')
    op.drop_table('playbooks')
    op.drop_table('topics')
    
    # Remove columns from messages
    op.drop_index('ix_messages_title', 'messages')
    op.drop_index('ix_messages_tags', 'messages')
    op.drop_column('messages', 'tags')
    op.drop_column('messages', 'description')
    op.drop_column('messages', 'title')
