"""
WAHA unified service for session management and message sending.

Consolidates session operations + message sending with rate limiting.
"""

from datetime import datetime

from robbot.adapters.external.waha_client import WAHAClient
from robbot.adapters.repositories.session_repository import SessionRepository
from robbot.config.settings import settings
from robbot.infra.redis.client import get_redis_client
import logging
from robbot.infra.db.models.session_model import WhatsAppSession
from robbot.schemas.waha import (
    MessageSentResponse,
    SendFileRequest,
    SendImageRequest,
    SendLocationRequest,
    SendTextRequest,
    SessionCreate,
    SessionOut,
    SessionStatus,
)

logger = logging.getLogger(__name__)


class WAHAService:
    """
    Unified WAHA service for sessions + messages.
    
    Responsibilities:
    - Session management (create, start, stop, status)
    - Message sending (text, image, file, location)
    - Rate limiting (anti-ban protection)
    - QR code generation
    """

    def __init__(
        self,
        session_repo: SessionRepository,
        waha_client: WAHAClient,
    ):
        self.session_repo = session_repo
        self.waha_client = waha_client
        self.redis_client = get_redis_client()
        self.session_name = settings.WAHA_SESSION_NAME

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

    # ========================================================================
    # MESSAGE SENDING WITH RATE LIMITING
    # ========================================================================

    def _get_rate_limit_key(self, chat_id: str) -> str:
        """Get Redis key for rate limiting."""
        return f"waha:ratelimit:{chat_id}"

    async def _check_rate_limit(self, chat_id: str) -> bool:
        """Check if rate limit allows sending message."""
        if not settings.WAHA_MESSAGES_PER_HOUR:
            return True

        key = self._get_rate_limit_key(chat_id)
        try:
            count = self.redis_client.get(key)
            if count and int(count) >= settings.WAHA_MESSAGES_PER_HOUR:
                logger.warning(
                    f"Rate limit exceeded for {chat_id}: {count}/{settings.WAHA_MESSAGES_PER_HOUR} msg/hour"
                )
                return False

            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 3600)
            pipe.execute()

            return True

        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            return True

    async def send_text(self, data: SendTextRequest) -> MessageSentResponse:
        """Send text message with anti-ban and rate limiting."""
        if not await self._check_rate_limit(data.chat_id):
            raise ValueError(
                f"Rate limit exceeded: max {settings.WAHA_MESSAGES_PER_HOUR} msg/hour"
            )

        response = await self.waha_client.send_text(
            session=self.session_name,
            chat_id=data.chat_id,
            text=data.text,
            apply_anti_ban=data.apply_anti_ban and settings.WAHA_ANTI_BAN_ENABLED,
            message_id_to_reply=data.reply_to,
        )

        logger.info(f"Text message sent to {data.chat_id}")

        return MessageSentResponse(
            message_id=response.get("id", ""),
            timestamp=response.get("timestamp", int(datetime.utcnow().timestamp())),
            chat_id=data.chat_id,
        )

    async def send_image(self, data: SendImageRequest) -> MessageSentResponse:
        """Send image message."""
        if not await self._check_rate_limit(data.chat_id):
            raise ValueError(
                f"Rate limit exceeded: max {settings.WAHA_MESSAGES_PER_HOUR} msg/hour"
            )

        response = await self.waha_client.send_image(
            session=self.session_name,
            chat_id=data.chat_id,
            file_url=data.file_url,
            caption=data.caption,
            apply_anti_ban=data.apply_anti_ban and settings.WAHA_ANTI_BAN_ENABLED,
        )

        logger.info(f"Image sent to {data.chat_id}")

        return MessageSentResponse(
            message_id=response.get("id", ""),
            timestamp=response.get("timestamp", int(datetime.utcnow().timestamp())),
            chat_id=data.chat_id,
        )

    async def send_file(self, data: SendFileRequest) -> MessageSentResponse:
        """Send file/document message."""
        if not await self._check_rate_limit(data.chat_id):
            raise ValueError(
                f"Rate limit exceeded: max {settings.WAHA_MESSAGES_PER_HOUR} msg/hour"
            )

        response = await self.waha_client.send_file(
            session=self.session_name,
            chat_id=data.chat_id,
            file_url=data.file_url,
            filename=data.filename,
            caption=data.caption,
        )

        logger.info(f"File sent to {data.chat_id}: {data.filename}")

        return MessageSentResponse(
            message_id=response.get("id", ""),
            timestamp=response.get("timestamp", int(datetime.utcnow().timestamp())),
            chat_id=data.chat_id,
        )

    async def send_location(self, data: SendLocationRequest) -> MessageSentResponse:
        """Send location message."""
        if not await self._check_rate_limit(data.chat_id):
            raise ValueError(
                f"Rate limit exceeded: max {settings.WAHA_MESSAGES_PER_HOUR} msg/hour"
            )

        response = await self.waha_client.send_location(
            session=self.session_name,
            chat_id=data.chat_id,
            latitude=data.latitude,
            longitude=data.longitude,
            title=data.title,
        )

        logger.info(f"Location sent to {data.chat_id}")

        return MessageSentResponse(
            message_id=response.get("id", ""),
            timestamp=response.get("timestamp", int(datetime.utcnow().timestamp())),
            chat_id=data.chat_id,
        )

    async def send_seen(self, chat_id: str, message_id: str) -> dict:
        """Mark message as seen (read receipt)."""
        return await self.waha_client.send_seen(
            session=self.session_name,
            chat_id=chat_id,
            message_id=message_id,
        )
