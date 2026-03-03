"""Repository for user persistence and retrieval operations."""

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.base_repository import BaseRepository
from robbot.infra.persistence.models.user_model import UserModel
from robbot.schemas.user import UserCreate


class UserRepository(BaseRepository[UserModel]):
    """
    Repository encapsulating DB access for users.
    """

    def __init__(self, db: Session):
        super().__init__(db, UserModel)

    def get_by_email(self, email: str) -> UserModel | None:
        """Retrieve user by email address."""
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def create_user(self, user_in: UserCreate, hashed_password: str) -> UserModel:
        """Create a new user (password is handled by CredentialRepository)."""
        user = UserModel(
            email=user_in.email,
            full_name=user_in.full_name,
            role=user_in.role,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user: UserModel) -> UserModel:
        """Update an existing user and commit changes."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_users(self, skip: int = 0, limit: int = 100) -> list[UserModel]:
        """Retrieve a paginated list of users."""
        return self.db.query(UserModel).offset(skip).limit(limit).all()

