"""
Notification Model - SQLAlchemy ORM model for in-app notifications.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from robbot.infra.db.base import Base


class NotificationModel(Base):
    """
    SQLAlchemy model for in-app notifications.
    
    Stores notifications for users about new leads, messages, and system events.
    """

    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Notification type: NEW_LEAD, NEW_MESSAGE, etc."
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<NotificationModel(id='{self.id}', user_id={self.user_id}, read={self.read})>"
