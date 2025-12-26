"""Repository for user persistence and retrieval operations."""

from typing import Optional

from sqlalchemy.orm import Session

from robbot.infra.db.models.user_model import UserModel
from robbot.schemas.user import UserCreate


class UserRepository:
    """
    Repository encapsulating DB access for users.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[UserModel]:
        """Retrieve user by email address."""
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        """Retrieve user by primary key ID."""
        return self.db.get(UserModel, user_id)

    def create_user(self, user_in: UserCreate, hashed_password: str) -> UserModel:
        """Create a new user including legacy `hashed_password` for backward compatibility."""
        user = UserModel(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=hashed_password,
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
