"""LID (Lightweight ID) Resolution Service.

Provides progressive resolution of WhatsApp LIDs to real phone numbers.

Strategy:
1. First message: Accept LID, try quick resolution (non-blocking)
2. When name detected: Try to save contact in WhatsApp + resolve LID
3. Periodic attempts: Keep trying to resolve LID over conversation lifetime
4. Update lead.phone_number when resolution succeeds

Based on WAHA-LID-RESOLUTION-PLAN.md
"""

import logging

from robbot.infra.persistence.repositories.lead_repository import LeadRepository

logger = logging.getLogger(__name__)


class LIDResolverService:
    """Service for progressive LID resolution."""

    LID_CACHE_PREFIX = "waha:lid_resolution:"
    LID_CACHE_TTL = 86400  # 24 hours

    def __init__(self, waha_client):
        """Initialize LID resolver.

        Args:
            waha_client: WAHA client instance for API calls
        """
        from robbot.config.settings import settings
        from robbot.infra.redis.client import get_redis_client

        self.waha_client = waha_client
        self.redis = get_redis_client()
        self.settings = settings

    def is_lid_format(self, identifier: str) -> bool:
        """Check if identifier is in LID format.

        Args:
            identifier: Phone or chat ID

        Returns:
            True if format is @lid
        """
        return "@lid" in identifier or (identifier and not identifier.endswith("@c.us") and len(identifier) > 10)

    async def try_resolve_lid(
        self,
        lid: str,
        session: str | None = None,
        timeout_seconds: float = 0.5,
    ) -> str | None:
        """Attempt to resolve LID to real phone number with timeout.

        Args:
            lid: LID identifier (e.g., '24988337893388@lid' or '24988337893388')
            session: Session name (default from settings)
            timeout_seconds: Maximum time to wait for resolution (default 0.5s)

        Returns:
            Real phone number (without @c.us) or None if resolution failed
        """
        import asyncio

        from robbot.core.custom_exceptions import WAHAError

        session = session or self.settings.WAHA_SESSION_NAME

        # Check cache first
        cache_key = f"{self.LID_CACHE_PREFIX}{lid}"
        cached_phone = self.redis.get(cache_key)
        if cached_phone:
            phone = cached_phone.decode() if isinstance(cached_phone, bytes) else cached_phone
            logger.debug("[LID RESOLVER] Cache hit: %s -> %s", lid, phone)
            return phone

        # Try resolution with timeout
        try:
            result = await asyncio.wait_for(
                self.waha_client.get_phone_by_lid(session, lid),
                timeout=timeout_seconds,
            )

            if result and result.get("pn"):
                phone = result["pn"].split("@")[0]
                # Cache successful resolution
                self.redis.setex(cache_key, self.LID_CACHE_TTL, phone)
                logger.info("[LID RESOLVER] Resolved: %s -> %s", lid, phone)
                return phone

        except WAHAError:
            # Expected error for not found
            pass
        except asyncio.TimeoutError:
            logger.warning("[LID RESOLVER] Timeout resolving LID: %s", lid)
        except Exception as e:
            logger.warning("[LID RESOLVER] Error resolving LID %s: %s", lid, str(e))

        return None

    async def try_resolve_phone_to_lid(
        self,
        phone: str,
        session: str | None = None,
    ) -> str | None:
        """Resolve phone number to LID (reverse lookup).

        Args:
            phone: Phone number
            session: Session name (default from settings)

        Returns:
            LID identifier or None if not found
        """
        session = session or self.settings.WAHA_SESSION_NAME

        try:
            result = await self.waha_client.get_lid_by_phone(session, phone)
            if result and result.get("lid"):
                lid = result["lid"].split("@")[0]
                logger.debug("[LID RESOLVER] Reverse resolved: %s -> %s", phone, lid)
                return lid
        except Exception:
            # Ignore all errors, just return None
            pass

        return None

    async def save_contact_to_whatsapp(
        self,
        phone_or_lid: str,
        name: str,
        session: str | None = None,
    ) -> bool:
        """Save contact to WhatsApp contact list using WAHA API.

        This is REQUIRED before LID resolution will work. WAHA can only
        resolve LIDs for contacts that exist in WhatsApp's contact list.

        Args:
            phone_or_lid: Phone number or LID (with or without @c.us/@lid)
            name: Contact name
            session: Session name (default from settings)

        Returns:
            True if contact was successfully saved
        """
        session_name = session or self.settings.WAHA_SESSION_NAME

        try:
            # Normalize chat_id format (keep @lid or @c.us suffix)
            chat_id = phone_or_lid if "@" in phone_or_lid else f"{phone_or_lid}@c.us"
            if "@lid" in phone_or_lid:
                # Keep LID format as-is
                chat_id = phone_or_lid if phone_or_lid.endswith("@lid") else f"{phone_or_lid}@lid"

            logger.info(
                "[LID RESOLVER] Saving contact to WhatsApp: chat_id='%s', name='%s'",
                chat_id,
                name,
            )

            # Call WAHA API to save contact
            result = await self.waha_client.update_contact(
                session=session_name,
                chat_id=chat_id,
                name=name,
            )

            logger.info(
                "[LID RESOLVER] Contact saved successfully: %s -> '%s' (result: %s)",
                chat_id,
                name,
                result,
            )
            return True

        except Exception as e:
            logger.error(
                "[LID RESOLVER] Failed to save contact %s: %s",
                phone_or_lid,
                str(e),
            )
            return False

    async def resolve_and_update_lead(
        self,
        lead_id: int,
        current_phone: str,
        lead_name: str | None,
        session,
    ) -> bool:
        """Try to resolve LID and update lead phone_number if successful.

        Complete resolution flow:
        1. Save contact to WhatsApp with LID+name
        2. Wait brief moment for WhatsApp sync
        3. Try to resolve LID to real phone
        4. Update lead.phone_number in database
        5. Update contact in WhatsApp with real phone

        Args:
            lead_id: Lead database ID
            current_phone: Current phone_number value (possibly LID)
            lead_name: Lead name (REQUIRED for contact saving)
            session: Database session

        Returns:
            True if phone_number was updated, False otherwise
        """
        import asyncio

        # Only attempt if current value looks like LID
        if not self.is_lid_format(current_phone):
            logger.debug("[LID RESOLVER] Phone already resolved: %s", current_phone)
            return False

        # Require name for contact saving (critical step!)
        if not lead_name or lead_name == "Lead":
            logger.debug(
                "[LID RESOLVER] Cannot resolve LID without name: lead_id=%s, phone=%s",
                lead_id,
                current_phone,
            )
            return False

        # STEP 1: Save contact to WhatsApp with LID+name
        # This is REQUIRED before WAHA can resolve the LID
        logger.info(
            "[LID RESOLVER] Starting resolution for lead #%s: lid='%s', name='%s'",
            lead_id,
            current_phone,
            lead_name,
        )

        contact_saved = await self.save_contact_to_whatsapp(current_phone, lead_name)

        if not contact_saved:
            logger.warning(
                "[LID RESOLVER] Failed to save contact to WhatsApp, aborting resolution"
            )
            return False

        # STEP 2: Wait brief moment for WhatsApp to sync contact
        logger.debug("[LID RESOLVER] Waiting 2s for WhatsApp contact sync...")
        await asyncio.sleep(2.0)

        # STEP 3: Try resolution
        resolved_phone = await self.try_resolve_lid(current_phone)

        if resolved_phone and resolved_phone != current_phone:
            # STEP 4: Update lead AND conversation in database
            lead_repo = LeadRepository(session)
            lead = lead_repo.get_by_id(lead_id)

            if lead:
                # Update lead phone_number
                lead.phone_number = resolved_phone
                
                # Update conversation phone_number AND chat_id if exists
                if lead.conversation:
                    lead.conversation.phone_number = resolved_phone
                    
                    # Also update chat_id (format: phone@c.us)
                    new_chat_id = f"{resolved_phone}@c.us"
                    old_chat_id = lead.conversation.chat_id
                    lead.conversation.chat_id = new_chat_id
                    
                    logger.info(
                        "[LID RESOLVER] 📊 Updated conversation: phone=%s, chat_id=%s -> %s",
                        resolved_phone,
                        old_chat_id,
                        new_chat_id,
                    )
                
                session.commit()

                logger.info(
                    "[LID RESOLVER] ✅ Updated lead #%s in DB: %s -> %s",
                    lead_id,
                    current_phone,
                    resolved_phone,
                )

                # STEP 5: Update contact in WhatsApp with real phone number
                await self.save_contact_to_whatsapp(resolved_phone, lead_name)

                return True
        else:
            logger.warning(
                "[LID RESOLVER] ❌ Resolution failed for lead #%s: lid='%s'",
                lead_id,
                current_phone,
            )

        return False


def get_lid_resolver(waha_client=None):
    """Factory function to get LID resolver instance.

    Args:
        waha_client: Optional WAHA client (creates new if not provided)

    Returns:
        LIDResolverService instance
    """
    if waha_client is None:
        from robbot.infra.integrations.waha.waha_client import get_waha_client

        waha_client = get_waha_client()

    return LIDResolverService(waha_client)

