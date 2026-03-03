"""ContextItemModel ORM for ordered content sequences."""

from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from robbot.infra.db.base import Base


class ContextItemModel(Base):
    """
    ContextItem entity linking contents to contexts in a specific order.
    """

    __tablename__ = "context_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    context_id = Column(String(36), ForeignKey("contexts.id", ondelete="CASCADE"), nullable=False, index=True)
    content_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Content template ID",
    )
    item_order = Column(Integer, nullable=False)  # 1, 2, 3...
    context_hint = Column(Text, nullable=True)  # When to use this step (for LLM)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    context = relationship("ContextModel", back_populates="items")
    content = relationship("ContentModel")

    __table_args__ = (UniqueConstraint("context_id", "item_order", name="uq_context_items_context_order"),)

    def __repr__(self) -> str:
        return f"<ContextItem id={self.id} context_id={self.context_id} order={self.item_order}>"
