"""ConversationMessage domain entity."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from robbot.domain.enums import MessageDirection


@dataclass
class ConversationMessage:
    """
    ConversationMessage entity representing a message in a conversation.
    
    Attributes:
        id: Unique message ID
        conversation_id: Associated conversation ID
        direction: Message direction (INBOUND/OUTBOUND)
        content: Message text content
        timestamp: Message timestamp
    """
    
    conversation_id: str
    direction: MessageDirection
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
