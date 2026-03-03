"""
Service for handling WAHA metadata resolution (LIDs, Contacts) synchronously.
Designed to be used by background jobs (RQ) that require blocking I/O.
"""

import logging
import httpx
from robbot.config.settings import settings
from robbot.infra.redis.client import get_redis_client

logger = logging.getLogger(__name__)


class WahaMetadataService:
    """
    Synchronous service for resolving WAHA metadata, specifically Logical IDs (LIDs).
    Uses Redis caching to minimize external API calls.
    """

    def __init__(self):
        self.redis = get_redis_client()
        self.base_url = settings.WAHA_URL.rstrip("/")
        self.api_key = settings.WAHA_API_KEY
        self.session = settings.WAHA_SESSION_NAME
        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        }
        # Connection Pooling: Persistent client for multiple calls per cycle
        self.client = httpx.Client(
            base_url=self.base_url,
            headers=self.headers,
            timeout=10.0
        )
        # Cache TTLs
        self.CACHE_TTL_LID = 3600  # 1 hour for direct mapping
        self.CACHE_TTL_REVERSE = 86400  # 24 hours for reverse mapping

    def get_lid_for_phone(self, phone: str) -> str | None:
        """
        Resolves a phone number to its WAHA LID (Logical ID).
        
        Flow:
        1. Check Redis cache (waha:target_phone_lid:{phone})
        2. If miss, call WAHA API:
           a. /api/contacts/check-exists (normalize phone)
           b. /api/{session}/lids/pn/{phone} (get LID)
        3. Cache results and return.

        Args:
            phone: Phone number to resolve (e.g., '5511999999999')

        Returns:
            LID string (e.g., '123456@lid') or None if not found/error.
        """
        # 1. Cache Check
        cache_key = f"waha:target_phone_lid:{phone}"
        cached_lid = self.redis.get(cache_key)

        if cached_lid:
            resolved_lid = cached_lid.decode("utf-8") if isinstance(cached_lid, bytes) else cached_lid
            # logger.debug("Cache HIT for LID: %s -> %s", phone, resolved_lid) # Verbose
            return resolved_lid

        # 2. External API Resolution
        try:
            # Step A: Normalize Phone via check-exists
            check_url = "/api/contacts/check-exists"
            check_params = {"session": self.session, "phone": phone}
            
            check_resp = self.client.get(check_url, params=check_params)
            
            normalized_phone = phone
            if check_resp.status_code == 200:
                data = check_resp.json()
                chat_id = data.get("chatId")
                if chat_id:
                    normalized_phone = chat_id.split("@")[0]

            # Step B: Get LID via lids/pn
            lids_url = f"/api/{self.session}/lids/pn/{normalized_phone}"
            lids_resp = self.client.get(lids_url)

            if lids_resp.status_code == 200:
                data = lids_resp.json()
                resolved_lid = data.get("lid")

                if resolved_lid:
                    lid_number = resolved_lid.split("@")[0] if "@" in resolved_lid else resolved_lid
                    
                    # 3. Cache Set
                    # Direct mapping: Phone -> LID (for this lookup)
                    self.redis.setex(cache_key, self.CACHE_TTL_LID, resolved_lid)
                    
                    # Reverse mapping: LID Number -> Phone (for incoming webhooks identification)
                    # Used to know that a message from 12345@lid is actually from 55119999
                    reverse_key = f"waha:dev_phone:{lid_number}"
                    self.redis.setex(reverse_key, self.CACHE_TTL_REVERSE, phone)

                    logger.info(
                        "[WAHA_METADATA] Resolved and cached LID: %s -> %s",
                        phone,
                        resolved_lid,
                    )
                    return resolved_lid
            
            elif lids_resp.status_code == 404:
                logger.warning("[WAHA_METADATA] LID not found for phone: %s", phone)
            else:
                logger.warning(
                    "[WAHA_METADATA] Failed to resolve LID: %s (status %s)", 
                    lids_resp.text, 
                    lids_resp.status_code
                )

        except httpx.HTTPError as e:
            logger.error("[WAHA_METADATA] HTTP/Network error resolving LID for %s: %s", phone, e)
        except Exception as e:
            logger.error("[WAHA_METADATA] Unexpected error resolving LID for %s: %s", phone, e)

        return None

    def get_all_chats(self, limit: int = 200, offset: int = 0) -> list[str]:
        """
        Retrieves all chat IDs from WAHA session synchronously.
        Attempts optimized /chats/overview first, falls back to /chats.

        Args:
            limit: Max chats to retrieve.
            offset: Pagination offset.

        Returns:
            List of chat IDs strings.
        """
        chat_ids = []
        try:
            # 1. Try Optimized Overview Endpoint
            overview_url = f"/api/{self.session}/chats/overview"
            params = {"limit": limit, "offset": offset}
            
            resp = self.client.get(overview_url, params=params)
            
            if resp.status_code == 200:
                try:
                    payload = resp.json()
                    # Overview payload is typically a list of chat objects
                    chat_ids = [c.get("id") for c in payload if c.get("id")]
                    return chat_ids
                except ValueError:
                    logger.warning("[WAHA_METADATA] Invalid JSON from chats/overview")

            else:
                logger.warning("[WAHA_METADATA] Failed to fetch chats/overview: %s", resp.status_code)

            # 2. Fallback to Standard Chats Endpoint
            chats_url = f"/api/{self.session}/chats"
            resp = self.client.get(chats_url, params=params)

            if resp.status_code == 200:
                try:
                    payload = resp.json()
                    chat_ids = [c.get("id") for c in payload if c.get("id")]
                except ValueError:
                    logger.warning("[WAHA_METADATA] Invalid JSON from chats")
            else:
                logger.error("[WAHA_METADATA] Failed to fetch chats: %s", resp.status_code)

        except httpx.HTTPError as e:
            logger.error("[WAHA_METADATA] HTTP error fetching chats: %s", e)
        except Exception as e:
            logger.error("[WAHA_METADATA] Unexpected error fetching chats: %s", e)

        return chat_ids

    def get_messages_from_chat(self, chat_id: str, limit: int = 10) -> list[dict]:
        """
        Retrieves messages for a specific chat synchronously.
        Handles errors gracefully (return empty list on failure).

        Args:
            chat_id: The chat ID (LID or phone ID).
            limit: Number of messages to retrieve.

        Returns:
            List of message dictionaries.
        """
        messages = []
        try:
            url = f"/api/{self.session}/chats/{chat_id}/messages"
            params = {"limit": limit}

            resp = self.client.get(url, params=params)

            if resp.status_code == 200:
                try:
                    messages = resp.json()
                except ValueError:
                    logger.warning("[WAHA_METADATA] Invalid JSON from messages endpoint for %s", chat_id)
            elif resp.status_code == 404:
                logger.debug("[WAHA_METADATA] Chat not found/empty messages: %s", chat_id)
            elif resp.status_code == 422:
                logger.warning("[WAHA_METADATA] Unprocessable Entity (session not ready?) for %s", chat_id)
            else:
                logger.warning("[WAHA_METADATA] Failed to fetch messages for %s: %s", chat_id, resp.status_code)

        except httpx.HTTPError as e:
            logger.error("[WAHA_METADATA] HTTP error fetching messages for %s: %s", chat_id, e)
        except Exception as e:
            logger.error("[WAHA_METADATA] Unexpected error fetching messages for %s: %s", chat_id, e)

        return messages

    def __del__(self):
        """Ensure the client is closed when the service is destroyed."""
        try:
            self.client.close()
        except Exception:
            pass
