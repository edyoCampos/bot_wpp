"""MessageLocationModel ORM for geographic location data."""

from uuid import uuid4

from sqlalchemy import Column, ForeignKey, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from robbot.infra.db.base import Base


class MessageLocationModel(Base):
    """Location coordinates linked to messages."""

    __tablename__ = "message_location"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    message_id = Column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    title = Column(String(500), nullable=True)

    # Relationship
    message = relationship("MessageModel", back_populates="location")

    def __repr__(self) -> str:
        return f"<MessageLocation id={self.id} message_id={self.message_id}>"
