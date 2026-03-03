"""Email verification service.

Manages the email verification flow:
- Generate verification tokens
- Send verification emails
- Validate received tokens
- Mark emails as verified
"""

import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.credential_repository import CredentialRepository
from robbot.infra.persistence.repositories.user_repository import UserRepository
from robbot.config.settings import settings
from robbot.core.custom_exceptions import AuthException


class EmailVerificationService:
    """Email verification service.

    Implements email verification flow to ensure valid addresses.
    """

    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
        self.credential_repo = CredentialRepository(db)
        self.user_repo = UserRepository(db)

    def generate_verification_token(self, user_id: int) -> str:
        """Generate a secure verification token for a user.

        Args:
            user_id: User ID to generate token for

        Returns:
            Generated verification token (32 hex characters)

        Raises:
            AuthException: If user or credential not found
        """
        credential = self.credential_repo.get_by_user_id(user_id)
        if not credential:
            raise AuthException("Credential not found")

        # Generate secure random token (32 bytes = 64 hex characters)
        token = secrets.token_urlsafe(32)

        # Store token and timestamp
        credential.email_verification_token = token
        credential.email_verification_sent_at = datetime.now(UTC)
        self.db.commit()

        return token

    def verify_email(self, token: str) -> int:
        """Verify email using verification token.

        Args:
            token: Verification token from email link

        Returns:
            User ID of verified user

        Raises:
            AuthException: If token is invalid, expired, or already used
        """
        credential = self.credential_repo.get_by_verification_token(token)
        if not credential:
            raise AuthException("Invalid verification token")

        # Check if already verified
        if credential.email_verified:
            raise AuthException("Email already verified")

        # Check token expiration (configurable)
        if credential.email_verification_sent_at:
            expiration_hours = settings.EMAIL_VERIFICATION_TOKEN_EXPIRATION_HOURS
            sent_at_aware = credential.email_verification_sent_at.replace(tzinfo=UTC)
            expiration = sent_at_aware + timedelta(hours=expiration_hours)
            if datetime.now(UTC) > expiration:
                raise AuthException("Verification token expired")

        # Mark as verified and invalidate token
        credential.email_verified = True
        credential.email_verification_token = None
        self.db.commit()

        return credential.user_id

    def resend_verification_email(self, email: str) -> str:
        """Resend verification email to user.

        Args:
            email: User's email address

        Returns:
            New verification token

        Raises:
            AuthException: If user not found or email already verified
        """
        user = self.user_repo.get_by_email(email)
        if not user:
            raise AuthException("User not found")

        credential = self.credential_repo.get_by_user_id(user.id)
        if not credential:
            raise AuthException("Credential not found")

        # Check if already verified
        if credential.email_verified:
            raise AuthException("Email already verified")

        # Apply rate limiting (configurable)
        min_interval_minutes = settings.EMAIL_VERIFICATION_RESEND_MIN_INTERVAL_MINUTES
        if min_interval_minutes and credential.email_verification_sent_at:
            min_interval = credential.email_verification_sent_at + timedelta(minutes=min_interval_minutes)
            if datetime.now(UTC) < min_interval:
                raise AuthException("Please wait before requesting another verification email")

        # Generate new token
        return self.generate_verification_token(user.id)

    def is_email_verified(self, user_id: int) -> bool:
        """Check if user's email is verified.

        Args:
            user_id: User ID to check

        Returns:
            True if email is verified, False otherwise
        """
        credential = self.credential_repo.get_by_user_id(user_id)
        if not credential:
            return False
        return credential.email_verified

