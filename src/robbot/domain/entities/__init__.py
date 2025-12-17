"""Domain entities for the application."""

from robbot.domain.entities.conversation import Conversation
from robbot.domain.entities.conversation_message import ConversationMessage
from robbot.domain.entities.lead import Lead
from robbot.domain.entities.lead_interaction import LeadInteraction
from robbot.domain.entities.llm_interaction import LLMInteraction

__all__ = [
    "Conversation",
    "ConversationMessage",
    "Lead",
    "LeadInteraction",
    "LLMInteraction",
]
