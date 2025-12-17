"""Repository for topic persistence and retrieval operations."""

from typing import Optional

from sqlalchemy.orm import Session

from robbot.domain.entities.topic import Topic
from robbot.infra.db.models.topic_model import TopicModel


class TopicRepository:
    """Repository encapsulating DB access for topics."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, topic: Topic) -> Topic:
        """Create a new topic."""
        model = TopicModel(
            id=topic.id,
            name=topic.name,
            description=topic.description,
            category=topic.category,
            active=topic.active,
            created_at=topic.created_at,
            updated_at=topic.updated_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, topic_id: str) -> Optional[Topic]:
        """Retrieve topic by ID."""
        model = self.db.query(TopicModel).filter(TopicModel.id == topic_id).first()
        return self._to_entity(model) if model else None

    def get_by_name(self, name: str) -> Optional[Topic]:
        """Retrieve topic by name."""
        model = self.db.query(TopicModel).filter(TopicModel.name == name).first()
        return self._to_entity(model) if model else None

    def list_all(self, active_only: bool = False, skip: int = 0, limit: int = 100) -> list[Topic]:
        """List all topics with optional filtering."""
        query = self.db.query(TopicModel)
        if active_only:
            query = query.filter(TopicModel.active == True)
        models = query.offset(skip).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def list_by_category(self, category: str, active_only: bool = False) -> list[Topic]:
        """List topics by category."""
        query = self.db.query(TopicModel).filter(TopicModel.category == category)
        if active_only:
            query = query.filter(TopicModel.active == True)
        models = query.all()
        return [self._to_entity(m) for m in models]

    def update(self, topic_id: str, **kwargs) -> Optional[Topic]:
        """Update topic fields."""
        model = self.db.query(TopicModel).filter(TopicModel.id == topic_id).first()
        if not model:
            return None
        
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def delete(self, topic_id: str) -> bool:
        """Delete topic (cascades to playbooks)."""
        model = self.db.query(TopicModel).filter(TopicModel.id == topic_id).first()
        if not model:
            return False
        
        self.db.delete(model)
        self.db.commit()
        return True

    def _to_entity(self, model: TopicModel) -> Topic:
        """Convert model to domain entity."""
        return Topic(
            id=model.id,
            name=model.name,
            description=model.description,
            category=model.category,
            active=model.active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
