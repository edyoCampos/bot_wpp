"""Conversation domain entity."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from robbot.domain.enums import ConversationStatus, LeadStatus

if TYPE_CHECKING:
    from robbot.domain.entities.lead import Lead


@dataclass
class Conversation:
    """
    Conversation entity representing a WhatsApp conversation.
    
    Attributes:
        id: Unique conversation ID
        chat_id: WhatsApp chat ID
        phone_number: Customer phone number
        status: Conversation status
        lead_status: Lead qualification status
        lead_id: Associated lead ID
        assigned_to_user_id: User ID if assigned
        created_at: Creation timestamp
        updated_at: Last update timestamp
        lead: Associated Lead entity (lazy loaded)
    """
    
    chat_id: str
    phone_number: str
    status: ConversationStatus
    lead_status: LeadStatus
    lead_id: Optional[str] = None
    assigned_to_user_id: Optional[int] = None
    is_urgent: bool = False
    notes: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    lead: Optional["Lead"] = None  # Lazy loaded relationship
