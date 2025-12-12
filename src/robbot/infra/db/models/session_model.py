"""WhatsApp session model (WAHA integration)."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from robbot.infra.db.base import Base


class WhatsAppSession(Base):
    """WhatsApp session managed by WAHA.

    Tracks connection status, QR code, and webhook configuration.
    For now, supports single global session (name='default').
    """

    __tablename__ = "whatsapp_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="STOPPED",
        comment="STOPPED, STARTING, SCAN_QR_CODE, WORKING, FAILED",
    )
    webhook_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    qr_code: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Base64 QR code image"
    )
    connected_phone: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="Connected WhatsApp number"
    )
    connected_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<WhatsAppSession(name='{self.name}', status='{self.status}')>"
