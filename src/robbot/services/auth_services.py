"""Authentication service implementing signup, login, token refresh and revocation."""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from robbot.adapters.repositories.token_repository import TokenRepository
from robbot.adapters.repositories.user_repository import UserRepository
from robbot.common.utils import send_email
from robbot.core import security
from robbot.core.exceptions import AuthException
from robbot.schemas.token import Token
from robbot.schemas.user import UserCreate, UserOut

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service layer that implements authentication business rules.
    """

    def __init__(self, db: Session):
        self.repo = UserRepository(db)
        self.token_repo = TokenRepository(db)

    def signup(self, payload: UserCreate) -> UserOut:
        """
        Register a new user with password policy, hashing and persistence.
        """
        existing = self.repo.get_by_email(payload.email)
        if existing:
            raise AuthException("User already exists")
        # Validate and hash password
        security.validate_password_policy(payload.password)
        hashed = security.get_password_hash(payload.password)
        user = self.repo.create_user(payload, hashed_password=hashed)
        return UserOut.model_validate(user)

    def authenticate_user(self, email: str, password: str) -> Optional[Token]:
        """
        Validate credentials and return tokens.
        """
        user = self.repo.get_by_email(email)
        if not user:
            logger.warning(f"Login failed: user not found for email {email}")
            return None
        if not user.is_active:
            logger.warning(f"Login failed: user {email} is inactive")
            return None
        if not security.verify_password(password, user.hashed_password):
            logger.warning(f"Login failed: invalid password for user {email}")
            return None
        logger.info(f"Login successful: user {email} (id={user.id})")
        tokens = security.create_access_refresh_tokens(str(user.id))
        return Token(**tokens)

    def refresh(self, refresh_token: str) -> Token:
        """
        Validate refresh token and return new pair.
        """
        if self.token_repo.is_revoked(refresh_token):
            raise AuthException("Token revoked")
        payload = security.decode_token(refresh_token, verify_exp=True)
        if payload.get("type") != "refresh":
            raise AuthException("Invalid token type")
        subject = payload.get("sub")
        tokens = security.create_access_refresh_tokens(subject)
        return Token(**tokens)

    def revoke_token(self, token: str) -> None:
        """
        Revoke token (refresh or access) by persisting it to DB.
        """
        # Persist revocation
        self.token_repo.revoke(token)
        logger.info(f"Token revoked successfully")

    def send_password_recovery(self, email: str) -> None:
        """
        Generates a short-lived token and sends to email. Token is a JWT with type 'pw-reset'.
        """
        user = self.repo.get_by_email(email)
        if not user:
            # Do not leak whether email exists
            return
        token = security.create_token_for_subject(
            str(user.id), minutes=15, token_type="pw-reset")
        send_email(to=email, subject="Password recovery",
                   body=f"Use this token to reset: {token}")

    def reset_password(self, token: str, new_password: str) -> None:
        """
        Reset password if token valid and meets policy.
        """
        payload = security.decode_token(token, verify_exp=True)
        if payload.get("type") != "pw-reset":
            raise AuthException("Invalid token for password reset")
        user_id = payload.get("sub")
        if not user_id:
            raise AuthException("Invalid token")
        user = self.repo.get_by_id(int(user_id))
        if not user:
            raise AuthException("User not found")
        # apply minimal password policy
        security.validate_password_policy(new_password)
        user.hashed_password = security.get_password_hash(new_password)
        self.repo.update_user(user)
