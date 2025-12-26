"""add_handoff_fields_to_conversations

Revision ID: 8c3f4d5e6a7b
Revises: 7b2c13997cdc
Create Date: 2025-12-17 10:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c3f4d5e6a7b'
down_revision: Union[str, Sequence[str], None] = '7b2c13997cdc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Adicionar novos campos para handoff bot→humano
    op.add_column('conversations', sa.Column('assigned_to', sa.Integer(), nullable=True))
    op.add_column('conversations', sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('conversations', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))
    # escalation_reason já existe na tabela conversations (criada em 5d3e9f1a2c4b)
    
    # Criar foreign key para assigned_to
    op.create_foreign_key(
        'fk_conversations_assigned_to_users',
        'conversations', 'users',
        ['assigned_to'], ['id'],
        ondelete='SET NULL'
    )
    
    # Criar índices para queries comuns
    op.create_index('idx_conversations_assigned_to', 'conversations', ['assigned_to'])
    op.create_index('idx_conversations_status', 'conversations', ['status'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_conversations_status', 'conversations')
    op.drop_index('idx_conversations_assigned_to', 'conversations')
    op.drop_constraint('fk_conversations_assigned_to_users', 'conversations', type_='foreignkey')
    # escalation_reason não foi adicionado nesta migração
    op.drop_column('conversations', 'completed_at')
    op.drop_column('conversations', 'assigned_at')
    op.drop_column('conversations', 'assigned_to')
