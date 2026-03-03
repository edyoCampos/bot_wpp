"""
WAHA unified service for session management and message sending.

Consolidates session operations + message sending with rate limiting.
"""

import logging
from datetime import UTC, datetime

from robbot.infra.integrations.waha.waha_client import WAHAClient
from robbot.infra.persistence.repositories.session_repository import SessionRepository
from robbot.config.settings import settings
from robbot.infra.persistence.models.session_model import WhatsAppSession
from robbot.infra.redis.client import get_redis_client
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
            ValueError: If session already exists in DB or WAHA
            WAHAError: For other WAHA API errors
        """
        # Check if session exists in DB
        existing = self.session_repo.get_by_name(data.name)
        if existing:
            raise ValueError(f"Session '{data.name}' already exists in database")

        # Determine webhook_url: prefer provided, else first config webhook, else default
        webhook_url = data.webhook_url or None
        if not webhook_url and data.config:
            try:
                webhooks = data.config.get("webhooks") or []
                if isinstance(webhooks, list) and webhooks:
                    webhook_url = webhooks[0].get("url")
            except Exception:
                webhook_url = None
        webhook_url = webhook_url or settings.WAHA_WEBHOOK_URL

        # Try to create session in WAHA
        try:
            waha_response = await self.waha_client.create_session(
                name=data.name,
                webhook_url=webhook_url,
                config=data.config or None,
            )
            logger.info("[INFO] WAHA session created: %s", waha_response)
        except Exception:
            # Re-raise; let controller handle (may be conflict if session exists in WAHA)
            raise

        # Save to DB
        session = self.session_repo.create(
            name=data.name,
            webhook_url=webhook_url,
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

        # Ensure webhooks are configured (message.any)
        try:
            await self.waha_client.update_session(
                name=name,
                webhook_url=settings.WAHA_WEBHOOK_URL,
            )
        except Exception as exc:  # noqa: BLE001 - non-fatal for start
            logger.warning(
                "[WARN] Failed to update WAHA session webhooks before start: %s",
                exc,
                extra={"session": name},
            )

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

        # Include qr_code alias for compatibility
        return SessionStatus(**status_data, qr_code=status_data.get("qr"))

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

        # Ensure webhooks are configured (message.any)
        try:
            await self.waha_client.update_session(
                name=name,
                webhook_url=settings.WAHA_WEBHOOK_URL,
            )
        except Exception as exc:  # noqa: BLE001 - non-fatal for restart
            logger.warning(
                "[WARN] Failed to update WAHA session webhooks before restart: %s",
                exc,
                extra={"session": name},
            )

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
            me_data = status_data.get("me")
            connected_phone = me_data.get("id") if isinstance(me_data, dict) else None
            self.session_repo.update_status(
                session_id=session.id,
                status=current_status,
                qr_code=status_data.get("qr"),
                connected_phone=connected_phone,
            )

        # Include qr_code alias for compatibility
        return SessionStatus(**status_data, qr_code=status_data.get("qr"))

    async def get_qr_code(self, name: str) -> dict:
        """Get QR code for session pairing.

        Args:
            name: Session name

        Returns:
            QR code data (base64 image)
        """
        return await self.waha_client.get_qr_code(name)

    async def list_sessions(self) -> list[dict]:
        """List all WAHA sessions (directly from WAHA).

        Returns:
            List of session dicts as provided by WAHA
        """
        return await self.waha_client.list_sessions()

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
            logger.info("Created default session: %s", settings.WAHA_SESSION_NAME)
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
                    "Rate limit exceeded for %s: %s/%s msg/hour", chat_id, count, settings.WAHA_MESSAGES_PER_HOUR
                )
                return False

            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 3600)
            pipe.execute()

            return True

        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error("[ERROR] Redis rate limit check failed: %s", e)
            return True

    async def send_text(self, data: SendTextRequest) -> MessageSentResponse:
        """Send text message with anti-ban and rate limiting."""
        if not await self._check_rate_limit(data.chat_id):
            raise ValueError(f"Rate limit exceeded: max {settings.WAHA_MESSAGES_PER_HOUR} msg/hour")

        response = await self.waha_client.send_text(
            session=self.session_name,
            chat_id=data.chat_id,
            text=data.text,
            apply_anti_ban=data.apply_anti_ban and settings.WAHA_ANTI_BAN_ENABLED,
            message_id_to_reply=data.reply_to,
        )

        logger.info("[INFO] Text message sent to %s", data.chat_id)

        return MessageSentResponse(
            message_id=response.get("id", ""),
            timestamp=response.get("timestamp", int(datetime.now(UTC).timestamp())),
            chat_id=data.chat_id,
        )

    async def send_image(self, data: SendImageRequest) -> MessageSentResponse:
        """Send image message."""
        if not await self._check_rate_limit(data.chat_id):
            raise ValueError(f"Rate limit exceeded: max {settings.WAHA_MESSAGES_PER_HOUR} msg/hour")

        response = await self.waha_client.send_image(
            session=self.session_name,
            chat_id=data.chat_id,
            file_url=data.file_url,
            caption=data.caption,
            apply_anti_ban=data.apply_anti_ban and settings.WAHA_ANTI_BAN_ENABLED,
        )

        logger.info("[INFO] Image sent to %s", data.chat_id)

        return MessageSentResponse(
            message_id=response.get("id", ""),
            timestamp=response.get("timestamp", int(datetime.now(UTC).timestamp())),
            chat_id=data.chat_id,
        )

    async def send_file(self, data: SendFileRequest) -> MessageSentResponse:
        """Send file/document message."""
        if not await self._check_rate_limit(data.chat_id):
            raise ValueError(f"Rate limit exceeded: max {settings.WAHA_MESSAGES_PER_HOUR} msg/hour")

        response = await self.waha_client.send_file(
            session=self.session_name,
            chat_id=data.chat_id,
            file_url=data.file_url,
            filename=data.filename,
            caption=data.caption,
        )

        logger.info("[INFO] File sent to %s: %s", data.chat_id, data.filename)

        return MessageSentResponse(
            message_id=response.get("id", ""),
            timestamp=response.get("timestamp", int(datetime.now(UTC).timestamp())),
            chat_id=data.chat_id,
        )

    async def send_location(self, data: SendLocationRequest) -> MessageSentResponse:
        """Send location message."""
        if not await self._check_rate_limit(data.chat_id):
            raise ValueError(f"Rate limit exceeded: max {settings.WAHA_MESSAGES_PER_HOUR} msg/hour")

        response = await self.waha_client.send_location(
            session=self.session_name,
            chat_id=data.chat_id,
            latitude=data.latitude,
            longitude=data.longitude,
            title=data.title,
        )

        logger.info("[INFO] Location sent to %s", data.chat_id)

        return MessageSentResponse(
            message_id=response.get("id", ""),
            timestamp=response.get("timestamp", int(datetime.now(UTC).timestamp())),
            chat_id=data.chat_id,
        )

    async def send_seen(self, chat_id: str, message_id: str) -> dict:
        """Mark message as seen (read receipt)."""
        return await self.waha_client.send_seen(
            session=self.session_name,
            chat_id=chat_id,
            message_id=message_id,
        )

