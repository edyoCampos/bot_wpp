from robbot.domain.conversations.conversation import Conversation
from robbot.infra.persistence.models.conversation_model import ConversationModel


class ConversationMapper:
    @staticmethod
    def to_domain(model: ConversationModel) -> Conversation:
        return Conversation(
            id=model.id,
            chat_id=model.chat_id,
            phone_number=model.phone_number,
            status=model.status,
            last_message_at=model.last_message_at,
            is_urgent=model.is_urgent,
            metadata=model.meta_data or {},
        )

    @staticmethod
    def to_model(entity: Conversation, model: ConversationModel | None = None) -> ConversationModel:
        if model is None:
            model = ConversationModel(id=entity.id)
            
        model.chat_id = entity.chat_id
        model.phone_number = entity.phone_number
        model.status = entity.status
        model.last_message_at = entity.last_message_at
        model.is_urgent = entity.is_urgent
        model.meta_data = entity.metadata
        
        return model
