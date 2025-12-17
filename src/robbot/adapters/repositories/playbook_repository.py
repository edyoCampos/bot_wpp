"""Repository for playbook persistence and retrieval operations."""

from typing import Optional

from sqlalchemy.orm import Session, joinedload

from robbot.domain.entities.playbook import Playbook
from robbot.infra.db.models.playbook_model import PlaybookModel


class PlaybookRepository:
    """Repository encapsulating DB access for playbooks."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, playbook: Playbook) -> Playbook:
        """Create a new playbook."""
        model = PlaybookModel(
            id=playbook.id,
            topic_id=playbook.topic_id,
            name=playbook.name,
            description=playbook.description,
            active=playbook.active,
            created_at=playbook.created_at,
            updated_at=playbook.updated_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, playbook_id: str, include_steps: bool = False) -> Optional[Playbook]:
        """Retrieve playbook by ID."""
        query = self.db.query(PlaybookModel)
        if include_steps:
            query = query.options(joinedload(PlaybookModel.steps))
        model = query.filter(PlaybookModel.id == playbook_id).first()
        return self._to_entity(model) if model else None

    def list_by_topic(self, topic_id: str, active_only: bool = False, include_steps: bool = False) -> list[Playbook]:
        """List playbooks by topic."""
        query = self.db.query(PlaybookModel).filter(PlaybookModel.topic_id == topic_id)
        if active_only:
            query = query.filter(PlaybookModel.active == True)
        if include_steps:
            query = query.options(joinedload(PlaybookModel.steps))
        models = query.all()
        return [self._to_entity(m) for m in models]

    def list_all(self, active_only: bool = False, skip: int = 0, limit: int = 100) -> list[Playbook]:
        """List all playbooks with optional filtering."""
        query = self.db.query(PlaybookModel)
        if active_only:
            query = query.filter(PlaybookModel.active == True)
        models = query.offset(skip).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def search_by_name(self, search_term: str, active_only: bool = False) -> list[Playbook]:
        """Search playbooks by name (case-insensitive partial match)."""
        query = self.db.query(PlaybookModel).filter(
            PlaybookModel.name.ilike(f"%{search_term}%")
        )
        if active_only:
            query = query.filter(PlaybookModel.active == True)
        models = query.all()
        return [self._to_entity(m) for m in models]

    def update(self, playbook_id: str, **kwargs) -> Optional[Playbook]:
        """Update playbook fields."""
        model = self.db.query(PlaybookModel).filter(PlaybookModel.id == playbook_id).first()
        if not model:
            return None
        
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def delete(self, playbook_id: str) -> bool:
        """Delete playbook (cascades to steps and embeddings)."""
        model = self.db.query(PlaybookModel).filter(PlaybookModel.id == playbook_id).first()
        if not model:
            return False
        
        self.db.delete(model)
        self.db.commit()
        return True

    def _to_entity(self, model: PlaybookModel) -> Playbook:
        """Convert model to domain entity."""
        return Playbook(
            id=model.id,
            topic_id=model.topic_id,
            name=model.name,
            description=model.description,
            active=model.active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
