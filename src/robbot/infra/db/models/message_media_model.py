"""MessageMediaModel ORM for media file attachments."""

from uuid import uuid4

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from robbot.infra.db.base import Base


class MessageMediaModel(Base):
    """Media file metadata linked to messages."""

    __tablename__ = "message_media"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    message_id = Column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mimetype = Column(String(255), nullable=False)
    filename = Column(String(500), nullable=False)
    url = Column(Text, nullable=False)

    # Relationship
    message = relationship("MessageModel", back_populates="media")

    def __repr__(self) -> str:
        return f"<MessageMedia id={self.id} message_id={self.message_id}>"
