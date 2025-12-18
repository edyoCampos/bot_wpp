"""
ConversationTag Model - SQLAlchemy ORM model for conversation-tag association.
"""

from datetime import datetime, timezone

from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from robbot.infra.db.base import Base


class ConversationTagModel(Base):
    """
    SQLAlchemy model for conversation-tag association (many-to-many).
    
    This is an association table that links conversations with their tags,
    allowing multiple tags per conversation and multiple conversations per tag.
    """

    __tablename__ = "conversation_tags"

    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        primary_key=True,
        comment="UUID of the conversation"
    )
    tag_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
        comment="ID of the tag"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="When the tag was applied to the conversation"
    )

    def __repr__(self) -> str:
        return f"<ConversationTagModel(conversation_id='{self.conversation_id}', tag_id={self.tag_id})>"
