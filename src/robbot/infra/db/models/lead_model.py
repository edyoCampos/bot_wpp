"""Lead model for managing sales prospects."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from robbot.infra.db.base import Base
from robbot.domain.enums import LeadStatus

if TYPE_CHECKING:
    from robbot.infra.db.models.conversation_model import ConversationModel
    from robbot.infra.db.models.lead_interaction_model import LeadInteractionModel
    from robbot.infra.db.models.user_model import UserModel


class LeadModel(Base):
    """Model for leads (prospects ready for scheduling).

    Tracks lead maturity, assignment, and conversion status.
    """

    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()), index=True
    )

    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        comment="One lead per conversation"
    )

    name: Mapped[str] = mapped_column(
        String(255), nullable=False,
        comment="Lead name"
    )

    phone_number: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True,
        comment="Contact phone number"
    )

    email: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
        comment="Email if provided"
    )

    status: Mapped[LeadStatus] = mapped_column(
        SQLEnum(LeadStatus),
        nullable=False,
        default=LeadStatus.NEW,
        index=True,
        comment="Lead maturity status"
    )

    maturity_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Lead score (0-100)"
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Internal notes about the lead"
    )

    assigned_to_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Assigned secretary user ID"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    converted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True,
        comment="When lead was converted (scheduled)"
    )

    # Relationships
    conversation: Mapped["ConversationModel"] = relationship(
        "ConversationModel", back_populates="lead"
    )
    assigned_to: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="assigned_leads", foreign_keys=[assigned_to_user_id]
    )
    interactions: Mapped[list["LeadInteractionModel"]] = relationship(
        "LeadInteractionModel", back_populates="lead", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "maturity_score >= 0 AND maturity_score <= 100",
            name="check_maturity_score_range"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<LeadModel(id='{self.id}', name='{self.name}', "
            f"status='{self.status}', score={self.maturity_score})>"
        )
