"""MessageModel ORM for generic message storage."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import CheckConstraint, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from robbot.infra.db.base import Base


class MessageModel(Base):
    """
    Generic message entity supporting text, media and location types.
    """

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    type = Column(
        String(50),
        nullable=False,
        index=True,
    )
    text = Column(Text, nullable=True)
    caption = Column(Text, nullable=True)
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
    media = relationship(
        "MessageMediaModel", back_populates="message", cascade="all, delete-orphan"
    )
    location = relationship(
        "MessageLocationModel",
        back_populates="message",
        cascade="all, delete-orphan",
        uselist=False,
    )

    __table_args__ = (
        CheckConstraint(
            "type IN ('text', 'image', 'voice', 'video', 'document', 'location')",
            name="message_type_check",
        ),
    )

    def __repr__(self) -> str:
        return f"<Message id={self.id} type={self.type}>"
