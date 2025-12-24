"""CredentialModel ORM for user authentication credentials.

This model is part of FASE 0 - Preparação.
It separates authentication credentials from user profile data,
following the Security Separation Principle.

Author: Sistema de Auditoria de Segurança
Date: 2025-12-23
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from robbot.infra.db.base import Base


class CredentialModel(Base):
    """User authentication credentials (separated from user profile).

    This table contains all authentication-related data, completely
    separated from user profile information.

    Rationale:
    - User is a domain entity (business concern)
    - Credential is a security entity (infrastructure concern)
    - This separation allows:
      * User queries without exposing credentials
      * Support for multiple auth methods (SSO, OAuth, magic links)
      * Granular audit of password changes
      * Improved performance (user queries don't join credentials)

    Migration Note:
    This model coexists with UserModel.hashed_password during FASE 0.
    Data migration happens in FASE 1.
    """

    __tablename__ = "credentials"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key to User (1:1 relationship)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )

    # Password Authentication
    hashed_password = Column(String(255), nullable=False)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)

    # Email Verification (FASE 4)
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_sent_at = Column(DateTime(timezone=True), nullable=True)

    # Password Reset
    reset_token = Column(String(255), nullable=True, index=True)
    reset_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    reset_token_used = Column(Boolean, default=False)

    # MFA (Multi-Factor Authentication) - FASE 5
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(255), nullable=True)  # TOTP secret (encrypted)
    backup_codes = Column(Text, nullable=True)  # JSON array of hashed backup codes

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("UserModel", back_populates="credential", uselist=False)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<CredentialModel(user_id={self.user_id}, email_verified={self.email_verified}, mfa_enabled={self.mfa_enabled})>"
