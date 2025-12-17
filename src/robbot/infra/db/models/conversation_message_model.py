"""Conversation message model for storing WhatsApp messages."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from robbot.infra.db.base import Base
from robbot.domain.enums import MessageDirection

if TYPE_CHECKING:
    from robbot.infra.db.models.conversation_model import ConversationModel


class ConversationMessageModel(Base):
    """Model for messages within conversations.

    Stores all inbound/outbound messages with metadata.
    """

    __tablename__ = "conversation_messages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()), index=True
    )

    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to conversations table"
    )

    direction: Mapped[MessageDirection] = mapped_column(
        SQLEnum(MessageDirection),
        nullable=False,
        index=True,
        comment="INBOUND or OUTBOUND"
    )

    from_phone: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="Sender phone number"
    )

    to_phone: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="Recipient phone number"
    )

    body: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Message text content"
    )

    media_url: Mapped[str | None] = mapped_column(
        String(512), nullable=True,
        comment="URL of media attachment if present"
    )

    waha_message_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True,
        comment="WAHA message ID for deduplication"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    # Relationship
    conversation: Mapped["ConversationModel"] = relationship(
        "ConversationModel", back_populates="messages"
    )

    def __repr__(self) -> str:
        return (
            f"<ConversationMessageModel(id='{self.id}', "
            f"direction='{self.direction}', body='{self.body[:30]}...')>"
        )
