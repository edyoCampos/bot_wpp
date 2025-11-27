"""User management service for CRUD operations."""

from sqlalchemy.orm import Session

from robbot.adapters.repositories.user_repository import UserRepository
from robbot.core.exceptions import NotFoundException
from robbot.infra.db.models.user_model import UserModel
from robbot.schemas.user import UserOut, UserUpdate


class UserService:
    """Service layer for user management operations."""

    def __init__(self, db: Session):
        self.repo = UserRepository(db)

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
