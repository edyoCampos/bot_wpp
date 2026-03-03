"""
Base repository with common CRUD operations.

Implements IRepository interface for polymorphic repository pattern.
Enables dependency injection and testability with mock repositories.

Resolves Issue #5: No Abstraction Layer for Repository Pattern
"""

import logging
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from robbot.core.interfaces import IRepository

logger = logging.getLogger("robbot.adapters.repositories.base_repository")

ModelType = TypeVar("ModelType")


class BaseRepository(IRepository[ModelType]):
    """
    Generic repository with common database operations.

    Implements IRepository interface for dependency injection.
    All services accept IRepository, not concrete BaseRepository.
    Enables testing with MockRepository without database.
    """

    def __init__(self, db: Session, model_class: type[ModelType]):
        """
        Initialize repository.

        Args:
            db: Database session
            model_class: SQLAlchemy ORM Model class
        """
        self.session = db
        self.db = db
        self.model_class = model_class

    def get_by_id(self, id: Any) -> ModelType | None:
        """
        Retrieve object by ID.

        Args:
            id: Primary key value

        Returns:
            Object or None if not found
        """
        return self.db.get(self.model_class, id)

    def create(self, obj: ModelType) -> ModelType:
        """
        Create and persist a new object.

        Args:
            obj: Object to create

        Returns:
            Created object with ID populated
        """
        self.db.add(obj)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelType, id: Any | None = None) -> ModelType | None:
        """
        Update an existing object.

        Args:
            obj: Updated object (must carry primary key) or pass id explicitly
            id: Optional primary key to fetch existing instance

        Returns:
            Updated object or None if not found
        """
        target_id = id if id is not None else getattr(obj, "id", None)
        if target_id is None:
            return None

        existing = self.get_by_id(target_id)
        if existing is None:
            return None

        # Merge attributes from obj into existing
        for key, value in obj.__dict__.items():
            if not key.startswith("_"):
                setattr(existing, key, value)

        self.db.flush()
        self.db.refresh(existing)
        return existing

    def delete(self, id: Any) -> bool:
        """
        Delete an object by ID.

        Args:
            id: Primary key to delete

        Returns:
            True if deleted, False if not found
        """
        obj = self.get_by_id(id)
        if obj is None:
            return False

        self.db.delete(obj)
        self.db.flush()
        return True

    def list_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """
        List all objects with pagination.

        Args:
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            List of objects
        """
        stmt = select(self.model_class).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def exists(self, id: Any) -> bool:
        """
        Check if object exists.

        Args:
            id: Primary key to check

        Returns:
            True if exists, False otherwise
        """
        return self.get_by_id(id) is not None

    def count(self) -> int:
        """
        Count total entities.

        Returns:
            Total number of objects
        """
        return self.db.query(self.model_class).count()
