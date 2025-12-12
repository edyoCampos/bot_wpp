"""WhatsApp message sending service with anti-ban logic."""

from datetime import datetime

from robbot.adapters.external.waha_client import WAHAClient
from robbot.config.settings import settings
import logging
from robbot.infra.redis.client import get_redis_client
from robbot.schemas.waha import (
    MessageSentResponse,
    SendFileRequest,
    SendImageRequest,
    SendLocationRequest,
    SendTextRequest,
)

logger = logging.getLogger(__name__)


class WhatsAppMessageService:
    """Business logic for WhatsApp message sending with rate limiting."""

    def __init__(self, waha_client: WAHAClient):
        """Initialize service.

        Args:
            waha_client: WAHA HTTP client
        """
        self.waha_client = waha_client
        self.redis_client = get_redis_client()
        self.session_name = settings.WAHA_SESSION_NAME

    def _get_rate_limit_key(self, chat_id: str) -> str:
        """Get Redis key for rate limiting.

        Args:
            chat_id: Chat ID

        Returns:
            Redis key
        """
        return f"waha:ratelimit:{chat_id}"

    async def _check_rate_limit(self, chat_id: str) -> bool:
        """Check if rate limit allows sending message.

        Args:
            chat_id: Chat ID

        Returns:
            True if allowed, False if rate limit exceeded
        """
        if not settings.WAHA_MESSAGES_PER_HOUR:
            return True  # Rate limiting disabled

        key = self._get_rate_limit_key(chat_id)
        try:
            # Get message count in last hour
            count = self.redis_client.get(key)
            if count and int(count) >= settings.WAHA_MESSAGES_PER_HOUR:
                logger.warning(
                    f"Rate limit exceeded for {chat_id}: {count}/{settings.WAHA_MESSAGES_PER_HOUR} msg/hour"
                )
                return False

            # Increment counter with 1h TTL
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 3600)  # 1 hour
            pipe.execute()

            return True

        except Exception as e:
            # Don't block on Redis errors
            logger.error(f"Redis rate limit check failed: {e}")
            return True

    async def send_text(
        self,
        data: SendTextRequest,
    ) -> MessageSentResponse:
        """Send text message with anti-ban and rate limiting.

        Args:
            data: Message data

        Returns:
            Sent message response

        Raises:
            ValueError: If rate limit exceeded
        """
        # Check rate limit
        if not await self._check_rate_limit(data.chat_id):
            raise ValueError(
                f"Rate limit exceeded: max {settings.WAHA_MESSAGES_PER_HOUR} msg/hour"
            )

        # Send with anti-ban if enabled
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
            timestamp=response.get("timestamp", int(
                datetime.utcnow().timestamp())),
            chat_id=data.chat_id,
        )

    async def send_image(
        self,
        data: SendImageRequest,
    ) -> MessageSentResponse:
        """Send image message.

        Args:
            data: Image data

        Returns:
            Sent message response
        """
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
            timestamp=response.get("timestamp", int(
                datetime.utcnow().timestamp())),
            chat_id=data.chat_id,
        )

    async def send_file(
        self,
        data: SendFileRequest,
    ) -> MessageSentResponse:
        """Send file/document message.

        Args:
            data: File data

        Returns:
            Sent message response
        """
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
            timestamp=response.get("timestamp", int(
                datetime.utcnow().timestamp())),
            chat_id=data.chat_id,
        )

    async def send_location(
        self,
        data: SendLocationRequest,
    ) -> MessageSentResponse:
        """Send location message.

        Args:
            data: Location data

        Returns:
            Sent message response
        """
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
            timestamp=response.get("timestamp", int(
                datetime.utcnow().timestamp())),
            chat_id=data.chat_id,
        )

    async def send_seen(self, chat_id: str, message_id: str) -> dict:
        """Mark message as seen (read receipt).

        Args:
            chat_id: Chat ID
            message_id: Message ID

        Returns:
            Success response
        """
        return await self.waha_client.send_seen(
            session=self.session_name,
            chat_id=chat_id,
            message_id=message_id,
        )
