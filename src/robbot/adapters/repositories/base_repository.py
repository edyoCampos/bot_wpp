"""Base repository with common CRUD operations."""

from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Generic repository with common database operations."""

    def __init__(self, db: Session, table=None, entity_class=None):
        """
        Initialize repository.
        
        Args:
            db: Database session
            table: SQLAlchemy Table (optional)
            entity_class: Entity class for mapping (optional)
        """
        self.session = db
        self.db = db
        self.table = table
        self.entity_class = entity_class
        self.model = entity_class  # Alias for compatibility

    def get_by_id(self, entity_id: int) -> Optional[ModelType]:
        """Get entity by ID."""
        return self.db.get(self.model, entity_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all entities with pagination."""
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def create(self, obj: ModelType) -> ModelType:
        """Create new entity."""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelType) -> ModelType:
        """Update existing entity."""
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelType) -> None:
        """Delete entity."""
        self.db.delete(obj)
        self.db.commit()

    def count(self) -> int:
        """Count total entities."""
        stmt = select(self.model)
        return len(list(self.db.scalars(stmt).all()))
