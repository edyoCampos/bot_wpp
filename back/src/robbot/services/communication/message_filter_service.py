"""
Service for filtering WhatsApp messages based on business rules and state (deduplication).
Ensures only valid, new, and allowed messages are processed.
"""
import logging
from typing import Set

from robbot.config.settings import settings
from robbot.infra.redis.client import get_redis_client

logger = logging.getLogger(__name__)


class MessageFilterService:
    """
    Filters inbound messages applying:
    - Self-message checks (fromMe)
    - DEV_MODE sender allow-listing
    - Deduplication (Redis check of message ID)
    """

    def __init__(self):
        self.redis = get_redis_client()
        self.last_check_was_processed = False

    def should_process(self, message: dict, allowed_senders: Set[str] | None = None) -> bool:
        """
        Determines if a message should be processed.
        
        Args:
            message: Raw message dict from WAHA.
            allowed_senders: Optional set of allowed sender IDs (for DEV mode).

        Returns:
            True if message is valid and new, False otherwise.
        """
        message_id = message.get("id")
        sender = message.get("from")

        # 1. Ignore messages sent by the bot itself
        # FIX(Bug1): Default MUST be False — if field is absent, assume NOT from bot.
        # Previous default of True silently rejected ALL messages without fromMe field.
        if message.get("fromMe", False):
            logger.debug("[FILTER] Rejeitada (fromMe=True): msg_id=%s", message_id)
            return False

        # 2. DEV Mode Restrictions
        if settings.DEV_MODE and allowed_senders:
            if not sender:
                logger.debug("[FILTER] Rejeitada (sem remetente): msg_id=%s", message_id)
                return False
                
            # Check exact match or phone number match
            sender_base = sender.split("@")[0]
            
            # Using set for O(1) lookup
            if sender not in allowed_senders and sender_base not in allowed_senders:
                logger.debug(
                    "[FILTER] Rejeitada (remetente não autorizado): sender=%s, sender_base=%s, allowed=%s",
                    sender, sender_base, allowed_senders
                )
                return False

        # 3. Deduplication Check (Idempotency)
        if not message_id:
            self.last_check_was_processed = False
            logger.debug("[FILTER] Rejeitada (sem message_id)")
            return False
        
        is_processed = self._is_processed(message_id)
        self.last_check_was_processed = is_processed
        
        if is_processed:
            # DEBUG level to avoid spam — dedup is normal in polling mode
            logger.debug("[FILTER] Rejeitada (já processada): msg_id=%s", message_id)
            return False

        return True

    def mark_as_processed(self, message_id: str):
        """Marks a message ID as processed in Redis with 24h TTL."""
        if message_id:
            key = f"waha:processed:{message_id}"
            self.redis.set(key, "1", ex=86400)

    def _is_processed(self, message_id: str) -> bool:
        """Checks if message ID exists in Redis."""
        key = f"waha:processed:{message_id}"
        return bool(self.redis.get(key))
