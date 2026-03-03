"""ContextModel ORM for content sequences."""

from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from robbot.infra.db.base import Base


class ContextModel(Base):
    """
    Context entity representing an organized sequence of items for a specific topic.
    """

    __tablename__ = "contexts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    topic = relationship("TopicModel", back_populates="contexts")
    items = relationship(
        "ContextItemModel",
        back_populates="context",
        cascade="all, delete-orphan",
        order_by="ContextItemModel.item_order",
    )
    embedding = relationship(
        "ContextEmbeddingModel", back_populates="context", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Context id={self.id} name={self.name} topic_id={self.topic_id}>"
