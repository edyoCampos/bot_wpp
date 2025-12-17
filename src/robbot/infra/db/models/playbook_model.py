"""PlaybookModel ORM for message sequences."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from robbot.infra.db.base import Base


class PlaybookModel(Base):
    """
    Playbook entity representing an organized sequence of messages for a specific topic.
    
    Example: "Apresentação Botox" playbook contains 5 steps with text, images, PDFs, videos
    that the LLM can use to respond to client inquiries about Botox.
    """

    __tablename__ = "playbooks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    topic_id = Column(
        String(36), 
        ForeignKey('topics.id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    topic = relationship("TopicModel", back_populates="playbooks")
    steps = relationship(
        "PlaybookStepModel", 
        back_populates="playbook", 
        cascade="all, delete-orphan",
        order_by="PlaybookStepModel.step_order"
    )
    embedding = relationship(
        "PlaybookEmbeddingModel", 
        back_populates="playbook", 
        cascade="all, delete-orphan",
        uselist=False
    )

    def __repr__(self) -> str:
        return f"<Playbook id={self.id} name={self.name} topic_id={self.topic_id}>"
