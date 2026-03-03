"""Repository for context persistence and retrieval operations."""

from sqlalchemy.orm import Session, joinedload

from robbot.infra.persistence.repositories.base_repository import BaseRepository
from robbot.infra.persistence.models.context_model import ContextModel


class ContextRepository(BaseRepository[ContextModel]):
    """Repository encapsulating DB access for contexts."""

    def __init__(self, db: Session):
        super().__init__(db, ContextModel)

    def get_by_topic_id(
        self, topic_id: str, active_only: bool = False, include_items: bool = False, limit: int = 100, offset: int = 0
    ) -> list[ContextModel]:
        """List contexts by topic with pagination.

        Args:
            topic_id: Topic ID to filter by
            active_only: If True, return only active contexts (default: False)
            include_items: If True, eager-load context items (default: False)
            limit: Maximum number of records to return (default: 100)
            offset: Number of records to skip (default: 0)

        Returns:
            List of context model instances
        """
        query = self.db.query(ContextModel).filter(ContextModel.topic_id == topic_id)
        if active_only:
            query = query.filter(ContextModel.active)
        if include_items:
            query = query.options(joinedload(ContextModel.items))
        return query.limit(limit).offset(offset).all()

    def get_by_name(
        self, search_term: str, active_only: bool = False, limit: int = 100, offset: int = 0
    ) -> list[ContextModel]:
        """Search contexts by name (case-insensitive partial match) with pagination.

        Args:
            search_term: Search term to match against context names
            active_only: If True, return only active contexts (default: False)
            limit: Maximum number of records to return (default: 100)
            offset: Number of records to skip (default: 0)

        Returns:
            List of context model instances matching the search term
        """
        query = self.db.query(ContextModel).filter(ContextModel.name.ilike(f"%{search_term}%"))
        if active_only:
            query = query.filter(ContextModel.active)
        return query.limit(limit).offset(offset).all()

    def get_active(self, skip: int = 0, limit: int = 100) -> list[ContextModel]:
        """List active contexts with pagination."""
        query = self.db.query(ContextModel).filter(ContextModel.active)
        return query.offset(skip).limit(limit).all()

    def list_by_topic(self, topic_id: str) -> list[ContextModel]:
        """List all contexts for a given topic."""
        return self.get_by_topic_id(topic_id, active_only=False)

