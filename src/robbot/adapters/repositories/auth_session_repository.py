"""Repositório para operações de persistência e recuperação de sessões de autenticação.

Gerencia todas as operações de banco de dados relacionadas a sessões de autenticação.
"""

from datetime import UTC, datetime
from typing import Optional

from sqlalchemy.orm import Session

from robbot.infra.db.models.auth_session_model import AuthSessionModel


class AuthSessionRepository:
    """Repository encapsulating DB access for authentication sessions."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create(
        self,
        user_id: int,
        refresh_token_jti: str,
        ip_address: str,
        user_agent: str | None,
        device_name: str | None,
        expires_at: datetime,
    ) -> AuthSessionModel:
        """Create new authentication session.

        Args:
            user_id: User ID
            refresh_token_jti: JWT ID of refresh token
            ip_address: Client IP address
            user_agent: Client user agent string
            device_name: Human-readable device name
            expires_at: Session expiration timestamp

        Returns:
            Created session model
        """
        session = AuthSessionModel(
            user_id=user_id,
            refresh_token_jti=refresh_token_jti,
            ip_address=ip_address,
            user_agent=user_agent,
            device_name=device_name,
            expires_at=expires_at,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_jti(self, jti: str) -> Optional[AuthSessionModel]:
        """Get session by refresh token JTI.

        Args:
            jti: JWT ID to search for

        Returns:
            Session model if found, None otherwise
        """
        return (
            self.db.query(AuthSessionModel)
            .filter(AuthSessionModel.refresh_token_jti == jti)
            .first()
        )

    def get_active_by_user_id(self, user_id: int) -> list[AuthSessionModel]:
        """Get all active (non-revoked, non-expired) sessions for user.

        Args:
            user_id: User ID

        Returns:
            List of active session models
        """
        now = datetime.now(UTC)
        return (
            self.db.query(AuthSessionModel)
            .filter(
                AuthSessionModel.user_id == user_id,
                AuthSessionModel.is_revoked == False,
                AuthSessionModel.expires_at > now,
            )
            .order_by(AuthSessionModel.last_used_at.desc())
            .all()
        )

    def get_all_by_user_id(self, user_id: int) -> list[AuthSessionModel]:
        """Get all sessions (active + revoked + expired) for user.

        Args:
            user_id: User ID

        Returns:
            List of all session models
        """
        return (
            self.db.query(AuthSessionModel)
            .filter(AuthSessionModel.user_id == user_id)
            .order_by(AuthSessionModel.created_at.desc())
            .all()
        )

    def update_last_used(
        self,
        session: AuthSessionModel,
        user_agent: str | None = None,
        ip_address: str | None = None,
        device_name: str | None = None,
    ) -> AuthSessionModel:
        """Update last_used_at timestamp and optionally device metadata.

        Args:
            session: Session model to update
            user_agent: Optional updated user agent
            ip_address: Optional updated IP address
            device_name: Optional updated device name

        Returns:
            Updated session model
        """
        session.last_used_at = datetime.now(UTC)
        if user_agent is not None:
            session.user_agent = user_agent
        if ip_address is not None:
            session.ip_address = ip_address
        if device_name is not None:
            session.device_name = device_name
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def revoke(
        self, session: AuthSessionModel, reason: str | None = None
    ) -> AuthSessionModel:
        """Revoke a session.

        Args:
            session: Session model to revoke
            reason: Revocation reason (e.g., "logout", "password_changed")

        Returns:
            Updated session model
        """
        session.is_revoked = True
        session.revoked_at = datetime.now(UTC)
        session.revocation_reason = reason
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def revoke_all_for_user(
        self, user_id: int, reason: str | None = None
    ) -> int:
        """Revoke all active sessions for user.

        Args:
            user_id: User ID
            reason: Revocation reason

        Returns:
            Number of sessions revoked
        """
        now = datetime.now(UTC)
        count = (
            self.db.query(AuthSessionModel)
            .filter(
                AuthSessionModel.user_id == user_id,
                AuthSessionModel.is_revoked == False,
            )
            .update(
                {
                    "is_revoked": True,
                    "revoked_at": now,
                    "revocation_reason": reason,
                },
                synchronize_session=False,
            )
        )
        self.db.commit()
        return count

    def delete_expired(self, before: datetime) -> int:
        """Delete expired sessions (cleanup job).

        Args:
            before: Delete sessions expired before this timestamp

        Returns:
            Number of sessions deleted
        """
        count = (
            self.db.query(AuthSessionModel)
            .filter(AuthSessionModel.expires_at < before)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return count

    def get_by_id(self, session_id: int) -> Optional[AuthSessionModel]:
        """Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session model if found, None otherwise
        """
        return self.db.get(AuthSessionModel, session_id)

    def revoke_by_id(
        self, session_id: int, user_id: int, reason: str | None = None
    ) -> bool:
        """Revoke session by ID (with user_id validation).

        Args:
            session_id: Session ID to revoke
            user_id: User ID (for authorization check)
            reason: Revocation reason

        Returns:
            True if session was revoked, False if not found or unauthorized
        """
        session = self.get_by_id(session_id)
        if not session or session.user_id != user_id:
            return False

        if session.is_revoked:
            return True  # Already revoked

        self.revoke(session, reason)
        return True
