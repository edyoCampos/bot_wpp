"""WAHA service for session management and orchestration."""

from robbot.adapters.external.waha_client import WAHAClient
from robbot.adapters.repositories.session_repository import SessionRepository
from robbot.config.settings import settings
import logging
from robbot.infra.db.models.session_model import WhatsAppSession
from robbot.schemas.waha import SessionCreate, SessionOut, SessionStatus

logger = logging.getLogger(__name__)


class WAHAService:
    """Business logic for WAHA session management."""

    def __init__(
        self,
        session_repo: SessionRepository,
        waha_client: WAHAClient,
    ):
        """Initialize service with dependencies.

        Args:
            session_repo: Session repository
            waha_client: WAHA HTTP client
        """
        self.session_repo = session_repo
        self.waha_client = waha_client

    async def create_session(
        self,
        data: SessionCreate,
    ) -> SessionOut:
        """Create new WhatsApp session.

        Args:
            data: Session creation data

        Returns:
            Created session

        Raises:
            ValueError: If session already exists
        """
        # Check if session exists in DB
        existing = self.session_repo.get_by_name(data.name)
        if existing:
            raise ValueError(f"Session '{data.name}' already exists")

        # Create session in WAHA
        waha_response = await self.waha_client.create_session(
            name=data.name,
            webhook_url=data.webhook_url or settings.WAHA_WEBHOOK_URL,
        )
        logger.info(f"WAHA session created: {waha_response}")

        # Save to DB
        session = self.session_repo.create(
            name=data.name,
            webhook_url=data.webhook_url or settings.WAHA_WEBHOOK_URL,
        )

        return SessionOut.model_validate(session)

    async def start_session(self, name: str) -> SessionStatus:
        """Start WhatsApp session (generate QR code).

        Args:
            name: Session name

        Returns:
            Session status with QR code

        Raises:
            ValueError: If session not found
        """
        session = self.session_repo.get_by_name(name)
        if not session:
            raise ValueError(f"Session '{name}' not found")

        # Start in WAHA
        await self.waha_client.start_session(name)

        # Get QR code
        status_data = await self.waha_client.get_session_status(name)

        # Update DB status
        self.session_repo.update_status(
            session_id=session.id,
            status=status_data.get("status", "STARTING"),
            qr_code=status_data.get("qr"),
        )

        return SessionStatus(**status_data)

    async def stop_session(self, name: str) -> dict:
        """Stop WhatsApp session.

        Args:
            name: Session name

        Returns:
            Success response
        """
        session = self.session_repo.get_by_name(name)
        if not session:
            raise ValueError(f"Session '{name}' not found")

        # Stop in WAHA
        result = await self.waha_client.stop_session(name)

        # Update DB
        self.session_repo.update_status(
            session_id=session.id,
            status="STOPPED",
        )

        return result

    async def restart_session(self, name: str) -> dict:
        """Restart WhatsApp session.

        Args:
            name: Session name

        Returns:
            Success response
        """
        session = self.session_repo.get_by_name(name)
        if not session:
            raise ValueError(f"Session '{name}' not found")

        # Restart in WAHA
        result = await self.waha_client.restart_session(name)

        # Update DB
        self.session_repo.update_status(
            session_id=session.id,
            status="STARTING",
        )

        return result

    async def get_session_status(self, name: str) -> SessionStatus:
        """Get current session status.

        Args:
            name: Session name

        Returns:
            Session status with connection info
        """
        session = self.session_repo.get_by_name(name)
        if not session:
            raise ValueError(f"Session '{name}' not found")

        # Get fresh status from WAHA
        status_data = await self.waha_client.get_session_status(name)

        # Update DB if status changed
        current_status = status_data.get("status")
        if current_status != session.status:
            self.session_repo.update_status(
                session_id=session.id,
                status=current_status,
                qr_code=status_data.get("qr"),
                connected_phone=status_data.get("me", {}).get("id"),
            )

        return SessionStatus(**status_data)

    async def get_qr_code(self, name: str) -> dict:
        """Get QR code for session pairing.

        Args:
            name: Session name

        Returns:
            QR code data (base64 image)
        """
        return await self.waha_client.get_qr_code(name)

    async def logout_session(self, name: str) -> dict:
        """Logout from WhatsApp (unlink device).

        Args:
            name: Session name

        Returns:
            Success response
        """
        session = self.session_repo.get_by_name(name)
        if not session:
            raise ValueError(f"Session '{name}' not found")

        # Logout in WAHA
        result = await self.waha_client.logout_session(name)

        # Update DB
        self.session_repo.update_status(
            session_id=session.id,
            status="STOPPED",
            connected_phone=None,
        )

        return result

    def get_or_create_default_session(self) -> WhatsAppSession:
        """Get or create default session in DB (helper for startup).

        Returns:
            Default session
        """
        session = self.session_repo.get_by_name(settings.WAHA_SESSION_NAME)
        if not session:
            session = self.session_repo.create(
                name=settings.WAHA_SESSION_NAME,
                webhook_url=settings.WAHA_WEBHOOK_URL,
            )
            logger.info(
                f"Created default session: {settings.WAHA_SESSION_NAME}")
        return session
