"""Conversation context model for storing structured conversation data."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from robbot.infra.db.base import Base

if TYPE_CHECKING:
    from robbot.infra.db.models.conversation_model import ConversationModel


class ConversationContextModel(Base):
    """Model for structured conversation context extracted by LLM.

    Stores parsed information like symptoms, concerns, intent, etc.
    """

    __tablename__ = "conversation_contexts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()), index=True
    )

    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        comment="One context per conversation"
    )

    patient_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
        comment="Extracted patient name if provided"
    )

    symptoms: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Structured symptoms data (e.g., {'pain': 'headache', 'duration': '2 days'})"
    )

    concerns: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Patient concerns and questions"
    )

    preferences: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
        comment="Scheduling preferences, location, etc."
    )

    intent_detected: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True,
        comment="Whether user intent was successfully detected"
    )

    intent_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True,
        comment="Type of intent (scheduling, question, complaint, etc.)"
    )

    summary: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="LLM-generated conversation summary"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationship
    conversation: Mapped["ConversationModel"] = relationship(
        "ConversationModel", back_populates="context"
    )

    def __repr__(self) -> str:
        return (
            f"<ConversationContextModel(id='{self.id}', "
            f"conversation_id='{self.conversation_id}', "
            f"intent_detected={self.intent_detected})>"
        )
