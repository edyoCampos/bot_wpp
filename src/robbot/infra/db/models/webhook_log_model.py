"""Webhook log model for WAHA events."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from robbot.infra.db.base import Base


class WebhookLog(Base):
    """Log of incoming webhooks from WAHA.

    Stores all webhook events for audit and debugging.
    Processed flag indicates if event was handled.
    """

    __tablename__ = "webhook_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_name: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, comment="message, message.ack, etc."
    )
    payload: Mapped[dict] = mapped_column(
        JSONB, nullable=False, comment="Full webhook payload"
    )
    processed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    error: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Processing error if any"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<WebhookLog(id={self.id}, event='{self.event_type}', processed={self.processed})>"
