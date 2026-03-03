"""MessageMediaModel ORM for media file attachments."""

from uuid import uuid4

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from robbot.infra.db.base import Base


class ContentMediaModel(Base):
    """Media file metadata linked to contents."""

    __tablename__ = "content_media"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    content_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mimetype = Column(String(255), nullable=False)
    filename = Column(String(500), nullable=False)
    url = Column(Text, nullable=False)

    # Relationship
    content = relationship("ContentModel", back_populates="media")

    def __repr__(self) -> str:
        return f"<ContentMedia id={self.id} content_id={self.content_id}>"
