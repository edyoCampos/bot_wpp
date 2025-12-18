"""
Tag Model - SQLAlchemy ORM model for conversation tags.
"""

from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from robbot.infra.db.base import Base


class TagModel(Base):
    """
    SQLAlchemy model for tags.
    
    Tags are used to categorize and organize conversations, allowing
    secretaries to filter and manage conversations more efficiently.
    """

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True,
        comment="Unique tag name (e.g., 'urgent', 'follow-up', 'vip')"
    )
    color: Mapped[str] = mapped_column(
        String(7), nullable=False,
        comment="Hex color code for UI display (e.g., '#FF5733')"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="Tag creation timestamp"
    )

    def __repr__(self) -> str:
        return f"<TagModel(id={self.id}, name='{self.name}', color='{self.color}')>"
