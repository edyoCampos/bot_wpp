"""TopicModel ORM for categorizing playbooks."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from robbot.infra.db.base import Base


class TopicModel(Base):
    """
    Topic entity for organizing playbooks by subject/context.
    
    Topics are generic containers (e.g., "Botox", "Preenchimento Labial", "Clareamento Dental")
    that can have multiple playbooks associated with them.
    """

    __tablename__ = "topics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)  # e.g., "Estética Facial", "Odontologia"
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
    playbooks = relationship(
        "PlaybookModel", 
        back_populates="topic", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Topic id={self.id} name={self.name}>"
