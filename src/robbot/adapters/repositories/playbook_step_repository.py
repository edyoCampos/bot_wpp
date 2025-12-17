"""Repository for playbook_step persistence and retrieval operations."""

from typing import Optional

from sqlalchemy.orm import Session, joinedload

from robbot.domain.entities.playbook_step import PlaybookStep
from robbot.infra.db.models.playbook_step_model import PlaybookStepModel


class PlaybookStepRepository:
    """Repository encapsulating DB access for playbook steps."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, step: PlaybookStep) -> PlaybookStep:
        """Create a new playbook step."""
        model = PlaybookStepModel(
            id=step.id,
            playbook_id=step.playbook_id,
            message_id=step.message_id,
            step_order=step.step_order,
            context_hint=step.context_hint,
            created_at=step.created_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, step_id: str) -> Optional[PlaybookStep]:
        """Retrieve step by ID."""
        model = self.db.query(PlaybookStepModel).filter(PlaybookStepModel.id == step_id).first()
        return self._to_entity(model) if model else None

    def list_by_playbook(self, playbook_id: str, include_messages: bool = False) -> list[PlaybookStep]:
        """List steps by playbook in order."""
        query = self.db.query(PlaybookStepModel).filter(
            PlaybookStepModel.playbook_id == playbook_id
        ).order_by(PlaybookStepModel.step_order)
        
        if include_messages:
            query = query.options(joinedload(PlaybookStepModel.message))
        
        models = query.all()
        return [self._to_entity(m) for m in models]

    def get_next_order(self, playbook_id: str) -> int:
        """Get next available step_order for a playbook."""
        max_order = self.db.query(PlaybookStepModel.step_order).filter(
            PlaybookStepModel.playbook_id == playbook_id
        ).order_by(PlaybookStepModel.step_order.desc()).first()
        
        return (max_order[0] + 1) if max_order else 1

    def update(self, step_id: str, **kwargs) -> Optional[PlaybookStep]:
        """Update step fields."""
        model = self.db.query(PlaybookStepModel).filter(PlaybookStepModel.id == step_id).first()
        if not model:
            return None
        
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def reorder_steps(self, playbook_id: str, step_id_order: list[tuple[str, int]]) -> bool:
        """Reorder multiple steps at once. step_id_order = [(step_id, new_order), ...]"""
        try:
            for step_id, new_order in step_id_order:
                model = self.db.query(PlaybookStepModel).filter(
                    PlaybookStepModel.id == step_id,
                    PlaybookStepModel.playbook_id == playbook_id
                ).first()
                if model:
                    model.step_order = new_order
            
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def delete(self, step_id: str) -> bool:
        """Delete playbook step."""
        model = self.db.query(PlaybookStepModel).filter(PlaybookStepModel.id == step_id).first()
        if not model:
            return False
        
        self.db.delete(model)
        self.db.commit()
        return True

    def _to_entity(self, model: PlaybookStepModel) -> PlaybookStep:
        """Convert model to domain entity."""
        return PlaybookStep(
            id=model.id,
            playbook_id=model.playbook_id,
            message_id=str(model.message_id),
            step_order=model.step_order,
            context_hint=model.context_hint,
            created_at=model.created_at,
        )
