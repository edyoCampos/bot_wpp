"""User management service for CRUD operations and admin actions."""

import contextlib

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.auth_session_repository import AuthSessionRepository
from robbot.infra.persistence.repositories.user_repository import UserRepository
from robbot.core.custom_exceptions import NotFoundException
from robbot.infra.persistence.models.user_model import UserModel
from robbot.schemas.user import UserOut, UserUpdate
from robbot.services.auth.audit_service import AuditService


class UserService:
    """Service layer for user management operations."""

    def __init__(self, db: Session):
        self.repo = UserRepository(db)
        self.session_repo = AuthSessionRepository(db)
        self.audit_svc = AuditService(db)

    def list_users(self, skip: int = 0, limit: int = 100) -> tuple[list[UserOut], int]:
        """
        Retrieve paginated list of users.
        Returns tuple of (users, total_count).
        """
        users = self.repo.list_users(skip=skip, limit=limit)
        total = self.repo.db.query(UserModel).count()
        return [UserOut.model_validate(u) for u in users], total

    def get_user(self, user_id: int) -> UserOut:
        """Retrieve a single user by ID."""
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        return UserOut.model_validate(user)

    def update_user(self, user_id: int, payload: UserUpdate) -> UserOut:
        """Update user profile fields."""
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")

        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.is_active is not None:
            user.is_active = payload.is_active

        updated = self.repo.update_user(user)
        return UserOut.model_validate(updated)

    def deactivate_user(self, user_id: int) -> None:
        """Soft delete user by setting is_active=False."""
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        user.is_active = False
        self.repo.update_user(user)

    def block_user(self, user_id: int, reason: str | None = None) -> UserOut:
        """Block a user: set is_active=False, revoke all sessions, audit."""
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        if user.is_active:
            user.is_active = False
            self.repo.update_user(user)
        # Revoke all active sessions
        self.session_repo.revoke_all_for_user(user_id, reason=reason or "admin_block")
        # Audit
        with contextlib.suppress(Exception):
            self.audit_svc.log_action(
                action="user_block",
                entity_type="User",
                entity_id=str(user_id),
                user_id=user_id,
                old_value={"is_active": True},
                new_value={"is_active": False, "reason": reason},
            )
        return UserOut.model_validate(user)

    def unblock_user(self, user_id: int, reason: str | None = None) -> UserOut:
        """Unblock a user: set is_active=True and audit."""
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        if not user.is_active:
            user.is_active = True
            self.repo.update_user(user)
        # Audit
        with contextlib.suppress(Exception):
            self.audit_svc.log_action(
                action="user_unblock",
                entity_type="User",
                entity_id=str(user_id),
                user_id=user_id,
                old_value={"is_active": False},
                new_value={"is_active": True, "reason": reason},
            )
        return UserOut.model_validate(user)

