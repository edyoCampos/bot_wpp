"""PlaybookStepModel ORM for ordered message sequences."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from robbot.infra.db.base import Base


class PlaybookStepModel(Base):
    """
    PlaybookStep entity linking messages to playbooks in a specific order.
    
    Each step represents a message that should be sent at a specific point
    in the playbook sequence.
    """

    __tablename__ = "playbook_steps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    playbook_id = Column(
        String(36), 
        ForeignKey('playbooks.id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    message_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('messages.id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    step_order = Column(Integer, nullable=False)  # 1, 2, 3...
    context_hint = Column(Text, nullable=True)  # When to use this step (for LLM)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    playbook = relationship("PlaybookModel", back_populates="steps")
    message = relationship("MessageModel")

    __table_args__ = (
        UniqueConstraint('playbook_id', 'step_order', name='uq_playbook_steps_playbook_order'),
    )

    def __repr__(self) -> str:
        return f"<PlaybookStep id={self.id} playbook_id={self.playbook_id} order={self.step_order}>"
