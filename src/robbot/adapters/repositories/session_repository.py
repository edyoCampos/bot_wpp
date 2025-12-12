"""Repository for WhatsApp session persistence."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from robbot.infra.db.models.session_model import WhatsAppSession


class SessionRepository:
    """Data access layer for WhatsApp sessions."""

    def __init__(self, db: Session):
        """Initialize repository with database session.

        Args:
            db: SQLAlchemy session
        """
        self.db = db

    def get_by_name(self, name: str) -> WhatsAppSession | None:
        """Get session by name.

        Args:
            name: Session name (e.g., 'default')

        Returns:
            Session or None if not found
        """
        stmt = select(WhatsAppSession).where(WhatsAppSession.name == name)
        return self.db.scalars(stmt).first()

    def get_active_session(self) -> WhatsAppSession | None:
        """Get active session (only one supported for now).

        Returns:
            Active session or None
        """
        stmt = (
            select(WhatsAppSession)
            .where(WhatsAppSession.is_active == True)
            .order_by(WhatsAppSession.created_at.desc())
        )
        return self.db.scalars(stmt).first()

    def create(
        self,
        name: str,
        webhook_url: str | None = None,
    ) -> WhatsAppSession:
        """Create new session.

        Args:
            name: Session name
            webhook_url: Webhook URL for events

        Returns:
            Created session
        """
        session = WhatsAppSession(
            name=name,
            webhook_url=webhook_url,
            status="STOPPED",
            is_active=True,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def update_status(
        self,
        session_id: int,
        status: str,
        qr_code: str | None = None,
        connected_phone: str | None = None,
    ) -> WhatsAppSession:
        """Update session status and metadata.

        Args:
            session_id: Session ID
            status: New status (STOPPED, STARTING, SCAN_QR_CODE, WORKING, FAILED)
            qr_code: Base64 QR code image
            connected_phone: Connected WhatsApp number

        Returns:
            Updated session
        """
        session = self.db.get(WhatsAppSession, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.status = status
        if qr_code is not None:
            session.qr_code = qr_code
        if connected_phone is not None:
            session.connected_phone = connected_phone

        self.db.commit()
        self.db.refresh(session)
        return session

    def deactivate(self, session_id: int) -> None:
        """Deactivate session.

        Args:
            session_id: Session ID
        """
        session = self.db.get(WhatsAppSession, session_id)
        if session:
            session.is_active = False
            self.db.commit()

    def count_active_sessions(self) -> int:
        """Count active sessions.

        Returns:
            Number of active sessions
        """
        stmt = select(WhatsAppSession).where(WhatsAppSession.is_active == True)
        return len(self.db.scalars(stmt).all())
