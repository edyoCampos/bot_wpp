"""Lead interaction model for tracking secretary activities."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from robbot.infra.db.base import Base
from robbot.domain.enums import InteractionType

if TYPE_CHECKING:
    from robbot.infra.db.models.lead_model import LeadModel
    from robbot.infra.db.models.user_model import UserModel


class LeadInteractionModel(Base):
    """Model for recording secretary interactions with leads.

    Provides audit trail of all activities related to a lead.
    """

    __tablename__ = "lead_interactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()), index=True
    )

    lead_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to leads table"
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who performed the interaction"
    )

    interaction_type: Mapped[InteractionType] = mapped_column(
        SQLEnum(InteractionType),
        nullable=False,
        index=True,
        comment="Type of interaction"
    )

    notes: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Details of the interaction"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    # Relationships
    lead: Mapped["LeadModel"] = relationship(
        "LeadModel", back_populates="interactions"
    )
    user: Mapped["UserModel"] = relationship("UserModel")

    def __repr__(self) -> str:
        return (
            f"<LeadInteractionModel(id='{self.id}', "
            f"type='{self.interaction_type}', lead_id='{self.lead_id}')>"
        )
