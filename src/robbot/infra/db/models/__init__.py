"""Database models package exports."""

from robbot.domain.enums import InteractionType
from robbot.infra.db.models.alert_model import AlertModel
from robbot.infra.db.models.auth_session_model import AuthSessionModel
from robbot.infra.db.models.conversation_context_model import ConversationContextModel
from robbot.infra.db.models.conversation_message_model import ConversationMessageModel
from robbot.infra.db.models.conversation_model import ConversationModel
from robbot.infra.db.models.conversation_tag_model import ConversationTagModel
from robbot.infra.db.models.credential_model import CredentialModel
from robbot.infra.db.models.lead_interaction_model import LeadInteractionModel
from robbot.infra.db.models.lead_model import LeadModel
from robbot.infra.db.models.llm_interaction_model import LLMInteractionModel
from robbot.infra.db.models.message_location_model import MessageLocationModel
from robbot.infra.db.models.message_media_model import MessageMediaModel
from robbot.infra.db.models.message_model import MessageModel
from robbot.infra.db.models.notification_model import NotificationModel
from robbot.infra.db.models.playbook_embedding_model import PlaybookEmbeddingModel
from robbot.infra.db.models.playbook_model import PlaybookModel
from robbot.infra.db.models.playbook_step_model import PlaybookStepModel
from robbot.infra.db.models.revoked_token_model import RevokedTokenModel
from robbot.infra.db.models.session_model import WhatsAppSession
from robbot.infra.db.models.tag_model import TagModel
from robbot.infra.db.models.topic_model import TopicModel
from robbot.infra.db.models.user_model import UserModel
from robbot.infra.db.models.webhook_log_model import WebhookLog

# Alias for relationship references (needed by other models)
User = UserModel

__all__ = [
    "AlertModel",
    "AuthSessionModel",
    "ConversationContextModel",
    "ConversationMessageModel",
    "ConversationModel",
    "ConversationTagModel",
    "CredentialModel",
    "InteractionType",
    "LeadInteractionModel",
    "LeadModel",
    "LLMInteractionModel",
    "MessageLocationModel",
    "MessageMediaModel",
    "MessageModel",
    "NotificationModel",
    "PlaybookEmbeddingModel",
    "PlaybookModel",
    "PlaybookStepModel",
    "RevokedTokenModel",
    "TagModel",
    "TopicModel",
    "User",
    "UserModel",
    "WhatsAppSession",
    "WebhookLog",
]
