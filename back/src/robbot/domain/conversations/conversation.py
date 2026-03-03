from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from robbot.domain.shared.enums import ConversationStatus


@dataclass
class Conversation:
    """
    Rich Domain entity for a conversation between robot and human.
    """

    id: str
    chat_id: str
    phone_number: str
    status: ConversationStatus = ConversationStatus.ACTIVE_BOT
    last_message_at: datetime = field(default_factory=datetime.utcnow)
    is_urgent: bool = False
    metadata: dict = field(default_factory=dict)

    def escalate(self, reason: str):
        """Escalate to human operator."""
        self.status = ConversationStatus.PENDING_HANDOFF
        self.metadata["escalation_reason"] = reason
        self.is_urgent = True

    def silence_bot(self):
        """Switch to active human mode."""
        self.status = ConversationStatus.ACTIVE_HUMAN

    def resume_bot(self):
        """Switch back to bot mode."""
        self.status = ConversationStatus.ACTIVE_BOT

    def mark_completed(self):
        """Mark as completed/resolved."""
        self.status = ConversationStatus.COMPLETED

    def close(self):
        """Close conversation."""
        self.status = ConversationStatus.CLOSED

    def mark_urgent(self):
        """Mark as urgent."""
        self.is_urgent = True
