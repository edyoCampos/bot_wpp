"""AuthSessionModel ORM for user authentication sessions.

This model is part of FASE 0 - Preparação.
It enables session management, allowing users to view and revoke active sessions.

Author: Sistema de Auditoria de Segurança
Date: 2025-12-23
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from robbot.infra.db.base import Base


class AuthSessionModel(Base):
    """User authentication sessions (JWT + metadata).

    This table stores metadata about active user sessions, enabling:
    - List all active sessions (web, mobile, etc.)
    - Revoke specific sessions (logout from specific device)
    - Revoke all sessions (logout from all devices)
    - Track device fingerprint (IP + User-Agent)
    - Detect suspicious activity (new location, new device)

    Note:
    - Sessions are created on login
    - Sessions are updated on token refresh (last_used_at)
    - Sessions are marked revoked on logout or explicit revocation
    - Expired sessions can be cleaned up by a background job

    Implementation in FASE 3.
    """

    __tablename__ = "auth_sessions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key to User
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Refresh Token (JWT ID)
    refresh_token_jti = Column(String(255), unique=True, nullable=False, index=True)

    # Device Information
    device_name = Column(String(255), nullable=True)  # e.g., "Chrome on Windows 10"
    ip_address = Column(String(45), nullable=False)  # IPv4 (15 chars) or IPv6 (45 chars)
    user_agent = Column(Text, nullable=True)

    # Session Lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Revocation
    is_revoked = Column(Boolean, default=False, nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revocation_reason = Column(
        String(255), nullable=True
    )  # e.g., "logout", "password_changed", "admin_action"

    # Relationships
    user = relationship("UserModel", back_populates="auth_sessions")

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<AuthSessionModel(id={self.id}, user_id={self.user_id}, device={self.device_name}, revoked={self.is_revoked})>"

    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now(self.expires_at.tzinfo) > self.expires_at

    @property
    def is_active(self) -> bool:
        """Check if session is active (not revoked and not expired)."""
        return not self.is_revoked and not self.is_expired
