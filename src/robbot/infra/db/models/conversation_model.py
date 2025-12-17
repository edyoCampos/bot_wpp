"""Conversation model for tracking WhatsApp conversations."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from robbot.infra.db.base import Base
from robbot.domain.enums import ConversationStatus, LeadStatus


class ConversationModel(Base):
    """Model for WhatsApp conversations.

    Tracks conversation state, lead status, and escalation info.
    """

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()), index=True
    )
    chat_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True,
        comment="WhatsApp chat ID (e.g., '5511999999999@c.us')"
    )
    phone_number: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )
    name: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Contact name"
    )
    
    status: Mapped[ConversationStatus] = mapped_column(
        SQLEnum(ConversationStatus),
        nullable=False,
        default=ConversationStatus.ACTIVE,
        index=True,
        comment="Current conversation status"
    )
    
    lead_status: Mapped[LeadStatus] = mapped_column(
        SQLEnum(LeadStatus),
        nullable=False,
        default=LeadStatus.NEW,
        index=True,
        comment="Lead maturity level"
    )
    
    escalation_reason: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="Reason for escalation (scheduling_request, issue, sentiment)"
    )
    
    escalated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True,
        comment="When conversation was escalated"
    )
    
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True,
        comment="Timestamp of last message"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    messages: Mapped[list["ConversationMessageModel"]] = relationship(
        "ConversationMessageModel",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    lead: Mapped["LeadModel"] = relationship(
        "LeadModel",
        back_populates="conversation",
        uselist=False,
        cascade="all, delete-orphan"
    )
    llm_interactions: Mapped[list["LLMInteractionModel"]] = relationship(
        "LLMInteractionModel",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )
    context: Mapped["ConversationContextModel"] = relationship(
        "ConversationContextModel",
        back_populates="conversation",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ConversationModel(id='{self.id}', chat_id='{self.chat_id}', status='{self.status}')>"
