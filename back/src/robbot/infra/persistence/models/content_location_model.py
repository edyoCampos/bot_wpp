"""MessageLocationModel ORM for geographic location data."""

from uuid import uuid4

from sqlalchemy import Column, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from robbot.infra.db.base import Base


class ContentLocationModel(Base):
    """Location coordinates linked to contents."""

    __tablename__ = "content_locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    content_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    title = Column(String(500), nullable=True)

    # Relationship
    content = relationship("ContentModel", back_populates="location")

    def __repr__(self) -> str:
        return f"<ContentLocation id={self.id} content_id={self.content_id}>"
