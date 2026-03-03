"""Database models package exports."""

from robbot.domain.shared.enums import InteractionType
from robbot.infra.persistence.models.audit_log_model import AuditLogModel
from robbot.infra.persistence.models.auth_session_model import AuthSessionModel
from robbot.infra.persistence.models.conversation_message_model import ConversationMessageModel
from robbot.infra.persistence.models.conversation_model import ConversationModel
from robbot.infra.persistence.models.conversation_tag_model import ConversationTagModel
from robbot.infra.persistence.models.credential_model import CredentialModel
from robbot.infra.persistence.models.lead_interaction_model import LeadInteractionModel
from robbot.infra.persistence.models.lead_model import LeadModel
from robbot.infra.persistence.models.llm_interaction_model import LLMInteractionModel
from robbot.infra.persistence.models.content_model import ContentModel
from robbot.infra.persistence.models.content_location_model import ContentLocationModel
from robbot.infra.persistence.models.content_media_model import ContentMediaModel
from robbot.infra.persistence.models.notification_model import NotificationModel
from robbot.infra.persistence.models.context_embedding_model import ContextEmbeddingModel
from robbot.infra.persistence.models.context_model import ContextModel
from robbot.infra.persistence.models.context_item_model import ContextItemModel
from robbot.infra.persistence.models.revoked_token_model import RevokedTokenModel
from robbot.infra.persistence.models.session_model import WhatsAppSession
from robbot.infra.persistence.models.tag_model import TagModel
from robbot.infra.persistence.models.topic_model import TopicModel
from robbot.infra.persistence.models.user_model import UserModel
from robbot.infra.persistence.models.webhook_log_model import WebhookLog

# Alias for relationship references (needed by other models)
User = UserModel

__all__ = [
    "AuditLogModel",
    "AuthSessionModel",
    "ConversationMessageModel",
    "ConversationModel",
    "ConversationTagModel",
    "CredentialModel",
    "InteractionType",
    "LeadInteractionModel",
    "LeadModel",
    "LLMInteractionModel",
    "ContentLocationModel",
    "ContentMediaModel",
    "ContentModel",
    "NotificationModel",
    "ContextEmbeddingModel",
    "ContextModel",
    "ContextItemModel",
    "RevokedTokenModel",
    "TagModel",
    "TopicModel",
    "User",
    "UserModel",
    "WhatsAppSession",
    "WebhookLog",
]

