"""Repository for credential persistence and retrieval operations.

This repository is part of FASE 0 - Preparação.
It handles all credential-related database operations.

Author: Sistema de Auditoria de Segurança
Date: 2025-12-23
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from robbot.infra.db.models.credential_model import CredentialModel


class CredentialRepository:
    """Repository encapsulating DB access for user credentials."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[CredentialModel]:
        """Retrieve credential by user ID."""
        return (
            self.db.query(CredentialModel).filter(CredentialModel.user_id == user_id).first()
        )

    def create(self, user_id: int, hashed_password: str) -> CredentialModel:
        """Create new credential for user.

        Args:
            user_id: User ID to associate credential with
            hashed_password: Bcrypt hashed password

        Returns:
            Created credential model
        """
        credential = CredentialModel(
            user_id=user_id,
            hashed_password=hashed_password,
            email_verified=False,
            mfa_enabled=False,
        )
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        return credential

    def update_password(
        self, credential: CredentialModel, new_hashed_password: str
    ) -> CredentialModel:
        """Update user password.

        Args:
            credential: Credential model to update
            new_hashed_password: New bcrypt hashed password

        Returns:
            Updated credential model
        """
        credential.hashed_password = new_hashed_password
        credential.password_changed_at = datetime.utcnow()
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        return credential

    def set_reset_token(
        self, credential: CredentialModel, token: str, expires_at: datetime
    ) -> CredentialModel:
        """Set password reset token.

        Args:
            credential: Credential model to update
            token: Reset token (hashed)
            expires_at: Token expiration timestamp

        Returns:
            Updated credential model
        """
        credential.reset_token = token
        credential.reset_token_expires_at = expires_at
        credential.reset_token_used = False
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        return credential

    def mark_reset_token_used(self, credential: CredentialModel) -> CredentialModel:
        """Mark reset token as used.

        Args:
            credential: Credential model to update

        Returns:
            Updated credential model
        """
        credential.reset_token_used = True
        credential.reset_token = None
        credential.reset_token_expires_at = None
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        return credential

    def get_by_reset_token(self, token: str) -> Optional[CredentialModel]:
        """Get credential by reset token.

        Args:
            token: Reset token to search for

        Returns:
            Credential model if found, None otherwise
        """
        return (
            self.db.query(CredentialModel)
            .filter(
                CredentialModel.reset_token == token,
                CredentialModel.reset_token_used == False,
                CredentialModel.reset_token_expires_at > datetime.utcnow(),
            )
            .first()
        )

    def verify_email(self, credential: CredentialModel) -> CredentialModel:
        """Mark email as verified.

        Args:
            credential: Credential model to update

        Returns:
            Updated credential model
        """
        credential.email_verified = True
        credential.email_verification_token = None
        credential.email_verification_sent_at = None
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        return credential

    def enable_mfa(
        self, credential: CredentialModel, secret: str, backup_codes: str
    ) -> CredentialModel:
        """Enable MFA for credential.

        Args:
            credential: Credential model to update
            secret: TOTP secret (encrypted)
            backup_codes: JSON array of hashed backup codes

        Returns:
            Updated credential model
        """
        credential.mfa_enabled = True
        credential.mfa_secret = secret
        credential.backup_codes = backup_codes
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        return credential

    def disable_mfa(self, credential: CredentialModel) -> CredentialModel:
        """Disable MFA for credential.

        Args:
            credential: Credential model to update

        Returns:
            Updated credential model
        """
        credential.mfa_enabled = False
        credential.mfa_secret = None
        credential.backup_codes = None
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        return credential
