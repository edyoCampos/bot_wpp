"""LLM interaction model for auditing AI requests."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from robbot.infra.db.base import Base
from robbot.domain.enums import LLMProvider

if TYPE_CHECKING:
    from robbot.infra.db.models.conversation_model import ConversationModel


class LLMInteractionModel(Base):
    """Model for logging LLM API interactions.

    Tracks token usage, latency, and full request/response for auditing.
    """

    __tablename__ = "llm_interactions"

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

    prompt: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Full prompt sent to LLM"
    )

    response: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Full response from LLM"
    )

    model_name: Mapped[str] = mapped_column(
        String(100), nullable=False,
        comment="Model identifier (e.g., 'gemini-1.5-pro')"
    )

    tokens_used: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
        comment="Total tokens used"
    )

    latency_ms: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
        comment="Request latency in milliseconds"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    # Relationship
    conversation: Mapped["ConversationModel"] = relationship(
        "ConversationModel", back_populates="llm_interactions"
    )

    def __repr__(self) -> str:
        return (
            f"<LLMInteractionModel(id='{self.id}', "
            f"model='{self.model_name}', tokens={self.tokens_used})>"
        )
