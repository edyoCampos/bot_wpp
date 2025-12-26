"""create credentials and auth_sessions tables

Revision ID: 15a122075f87
Revises: 007ad6343e57
Create Date: 2025-12-24 14:09:14.983809

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15a122075f87'
down_revision: Union[str, Sequence[str], None] = '007ad6343e57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.
    
    FASE 1 - Task 1.1: Create credentials and auth_sessions tables.
    Migrate hashed_password from users to credentials.
    """
    # ========================================================================
    # STEP 1: Create credentials table
    # ========================================================================
    op.create_table(
        'credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        
        # Password Authentication
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True),
        
        # Email Verification (FASE 4)
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_verification_token', sa.String(length=255), nullable=True),
        sa.Column('email_verification_sent_at', sa.DateTime(timezone=True), nullable=True),
        
        # Password Reset
        sa.Column('reset_token', sa.String(length=255), nullable=True),
        sa.Column('reset_token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reset_token_used', sa.Boolean(), nullable=True, server_default='false'),
        
        # MFA (FASE 5)
        sa.Column('mfa_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('mfa_secret', sa.String(length=255), nullable=True),
        sa.Column('backup_codes', sa.Text(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # Primary Key
        sa.PrimaryKeyConstraint('id'),
        
        # Foreign Key to users
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        
        # Unique constraint (1:1 relationship)
        sa.UniqueConstraint('user_id', name='uq_credentials_user_id')
    )
    
    # Indexes
    op.create_index('ix_credentials_id', 'credentials', ['id'])
    op.create_index('ix_credentials_user_id', 'credentials', ['user_id'])
    op.create_index('ix_credentials_reset_token', 'credentials', ['reset_token'])
    
    # ========================================================================
    # STEP 2: Migrate data from users.hashed_password to credentials
    # ========================================================================
    op.execute("""
        INSERT INTO credentials (user_id, hashed_password, email_verified, created_at, updated_at)
        SELECT 
            id as user_id,
            hashed_password,
            false as email_verified,
            created_at,
            created_at as updated_at
        FROM users
        WHERE hashed_password IS NOT NULL
    """)
    
    # ========================================================================
    # STEP 3: Create auth_sessions table
    # ========================================================================
    op.create_table(
        'auth_sessions',
        sa.Column('id', sa.String(length=64), nullable=False),  # UUID as string
        sa.Column('user_id', sa.Integer(), nullable=False),
        
        # Session Data
        sa.Column('refresh_token_hash', sa.String(length=64), nullable=False),
        sa.Column('device_info', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        
        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoke_reason', sa.String(length=255), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        
        # Primary Key
        sa.PrimaryKeyConstraint('id'),
        
        # Foreign Key to users
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Indexes
    op.create_index('ix_auth_sessions_id', 'auth_sessions', ['id'])
    op.create_index('ix_auth_sessions_user_id', 'auth_sessions', ['user_id'])
    op.create_index('ix_auth_sessions_refresh_token_hash', 'auth_sessions', ['refresh_token_hash'])
    op.create_index('ix_auth_sessions_is_active', 'auth_sessions', ['is_active'])
    op.create_index('ix_auth_sessions_expires_at', 'auth_sessions', ['expires_at'])
    
    # ========================================================================
    # STEP 4: Drop hashed_password from users (DEFERRED to avoid breaking existing code)
    # This will be done after all services are updated to use CredentialService
    # ========================================================================
    # NOTE: Commented out for safety during FASE 1
    # op.drop_column('users', 'hashed_password')


def downgrade() -> None:
    """Downgrade schema.
    
    Restore hashed_password to users table and drop new tables.
    """
    # ========================================================================
    # STEP 1: Restore hashed_password column to users (if it was dropped)
    # ========================================================================
    # NOTE: Uncomment when STEP 4 in upgrade() is uncommented
    # op.add_column('users', sa.Column('hashed_password', sa.String(length=255), nullable=True))
    
    # ========================================================================
    # STEP 2: Migrate data back from credentials to users
    # ========================================================================
    op.execute("""
        UPDATE users u
        SET hashed_password = c.hashed_password
        FROM credentials c
        WHERE u.id = c.user_id
    """)
    
    # ========================================================================
    # STEP 3: Drop auth_sessions table
    # ========================================================================
    op.drop_index('ix_auth_sessions_expires_at', 'auth_sessions')
    op.drop_index('ix_auth_sessions_is_active', 'auth_sessions')
    op.drop_index('ix_auth_sessions_refresh_token_hash', 'auth_sessions')
    op.drop_index('ix_auth_sessions_user_id', 'auth_sessions')
    op.drop_index('ix_auth_sessions_id', 'auth_sessions')
    op.drop_table('auth_sessions')
    
    # ========================================================================
    # STEP 4: Drop credentials table
    # ========================================================================
    op.drop_index('ix_credentials_reset_token', 'credentials')
    op.drop_index('ix_credentials_user_id', 'credentials')
    op.drop_index('ix_credentials_id', 'credentials')
    op.drop_table('credentials')
