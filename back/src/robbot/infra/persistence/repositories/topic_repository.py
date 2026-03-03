"""Repository for topic persistence and retrieval operations."""

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.base_repository import BaseRepository
from robbot.infra.persistence.models.topic_model import TopicModel


class TopicRepository(BaseRepository[TopicModel]):
    """Repository encapsulating DB access for topics."""

    def __init__(self, db: Session):
        super().__init__(db, TopicModel)

    def get_by_name(self, name: str) -> TopicModel | None:
        """Retrieve topic by name."""
        return self.db.query(TopicModel).filter(TopicModel.name == name).first()

    def list_all(self, active_only: bool = False, skip: int = 0, limit: int = 100) -> list[TopicModel]:
        """List all topics with optional filtering."""
        query = self.db.query(TopicModel)
        if active_only:
            query = query.filter(TopicModel.active)
        return query.offset(skip).limit(limit).all()

    def list_by_category(
        self, category: str, active_only: bool = False, limit: int = 100, offset: int = 0
    ) -> list[TopicModel]:
        """List topics by category with pagination.

        Args:
            category: Topic category to filter by
            active_only: If True, return only active topics (default: False)
            limit: Maximum number of records to return (default: 100)
            offset: Number of records to skip (default: 0)

        Returns:
            List of topic model instances
        """
        query = self.db.query(TopicModel).filter(TopicModel.category == category)
        if active_only:
            query = query.filter(TopicModel.active)
        return query.limit(limit).offset(offset).all()

