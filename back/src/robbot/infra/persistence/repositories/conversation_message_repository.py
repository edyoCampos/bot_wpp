"""Repository for ConversationMessage entity."""

import logging

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.base_repository import BaseRepository
from robbot.infra.persistence.models.conversation_message_model import ConversationMessageModel

logger = logging.getLogger(__name__)


class ConversationMessageRepository(BaseRepository[ConversationMessageModel]):
    """Repository for conversation messages CRUD operations."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        super().__init__(session, ConversationMessageModel)

    def get_by_conversation(self, conversation_id: str, limit: int = 50) -> list[ConversationMessageModel]:
        """
        Get messages by conversation ID.

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages

        Returns:
            List of messages ordered by timestamp
        """
        return (
            self.session.query(ConversationMessageModel)
            .filter_by(conversation_id=conversation_id)
            .order_by(ConversationMessageModel.created_at.desc())
            .limit(limit)
            .all()
        )

