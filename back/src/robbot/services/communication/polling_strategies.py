"""
Strategy definitions for WAHA Chat Polling.
Allows dynamic switching of polling behavior based on environment (DEV vs PROD).
"""
import logging
from abc import ABC, abstractmethod
from typing import List

from robbot.config.settings import settings
from robbot.services.communication.waha_metadata_service import WahaMetadataService

logger = logging.getLogger(__name__)


class PollingStrategy(ABC):
    """Abstract base strategy for fetching target chat IDs to monitor."""
    
    @abstractmethod
    def get_target_chats(self) -> List[str]:
        """Returns a list of Chat IDs (LIDs or Phone IDs) to monitor."""
        pass


class DevPollingStrategy(PollingStrategy):
    """
    DEV MODE STRATEGY:
    Only polls explicitly allowed phone numbers defined in settings.dev_phone_list.
    Automatically resolves LIDs for these numbers using metadata service.
    """

    def __init__(self, metadata_service: WahaMetadataService):
        self.metadata_service = metadata_service

    def get_target_chats(self) -> List[str]:
        target_chats: List[str] = []
        
        if not settings.dev_phone_list:
            logger.warning("[POLLING][DEV] No DEV_PHONE_NUMBERS configured.")
            return []

        for phone in settings.dev_phone_list:
            # Uses optimized cached fetch logic
            lid = self.metadata_service.get_lid_for_phone(phone)
            
            if lid:
                target_chats.append(lid)
            else:
                # If LID resolution fails, we might still want to try polling the original phone ID
                # or just log and skip. For robustness, let's try the original phone if LID fails,
                # assuming it might be a standard @c.us chat.
                logger.debug("[POLLING][DEV] LID resolution failed for %s. Using raw phone ID.", phone)
                target_chats.append(f"{phone}@c.us" if "@" not in phone else phone)
                
        return target_chats


class ProdPollingStrategy(PollingStrategy):
    """
    PROD MODE STRATEGY:
    Polls ALL active chats from the session, prioritizing recent activity.
    """

    def __init__(self, metadata_service: WahaMetadataService):
         self.metadata_service = metadata_service

    def get_target_chats(self) -> List[str]:
        # Fetch all chats from WAHA session
        chats = self.metadata_service.get_all_chats(limit=200)
        if not chats:
            logger.info("[POLLING][PROD] No active chats found.")
        return chats


def get_polling_strategy() -> PollingStrategy:
    """Factory to get the correct strategy based on current settings."""
    metadata_service = WahaMetadataService()
    
    if settings.DEV_MODE:
        logger.info("[POLLING] Using DEV Strategy (Restricted Senders)")
        return DevPollingStrategy(metadata_service)
    
    logger.info("[POLLING] Using PROD Strategy (All Chats)")
    return ProdPollingStrategy(metadata_service)
