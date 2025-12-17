"""Repository for ConversationMessage entity."""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from robbot.domain.entities.conversation_message import ConversationMessage
from robbot.domain.enums import MessageDirection
from robbot.infra.db.models.conversation_message_model import ConversationMessageModel

logger = logging.getLogger(__name__)


class ConversationMessageRepository:
    """Repository for conversation messages CRUD operations."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        self.session = session

    def create(self, message: ConversationMessage) -> ConversationMessage:
        """
        Create new conversation message.
        
        Args:
            message: ConversationMessage entity
            
        Returns:
            Created entity with ID
        """
        model = ConversationMessageModel(
            id=message.id,
            conversation_id=message.conversation_id,
            direction=message.direction,
            content=message.content,
            timestamp=message.timestamp or datetime.now(timezone.utc),
        )
        
        self.session.add(model)
        self.session.flush()
        
        logger.info(f"✓ ConversationMessage created (id={model.id})")
        
        return self._to_entity(model)

    def get_by_id(self, message_id: str) -> Optional[ConversationMessage]:
        """
        Get conversation message by ID.
        
        Args:
            message_id: Message ID
            
        Returns:
            ConversationMessage or None
        """
        model = self.session.query(ConversationMessageModel).filter_by(id=message_id).first()
        
        if model:
            return self._to_entity(model)
        
        return None

    def get_by_conversation(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> list[ConversationMessage]:
        """
        Get messages by conversation ID.
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages
            
        Returns:
            List of messages ordered by timestamp
        """
        models = (
            self.session.query(ConversationMessageModel)
            .filter_by(conversation_id=conversation_id)
            .order_by(ConversationMessageModel.timestamp.desc())
            .limit(limit)
            .all()
        )
        
        return [self._to_entity(m) for m in models]

    def get_all(self) -> list[ConversationMessage]:
        """
        Get all conversation messages.
        
        Returns:
            List of all messages
        """
        models = self.session.query(ConversationMessageModel).all()
        return [self._to_entity(m) for m in models]

    def update(self, message: ConversationMessage) -> ConversationMessage:
        """
        Update existing conversation message.
        
        Args:
            message: ConversationMessage entity
            
        Returns:
            Updated entity
        """
        model = self.session.query(ConversationMessageModel).filter_by(id=message.id).first()
        
        if not model:
            raise ValueError(f"ConversationMessage {message.id} not found")
        
        model.content = message.content
        model.direction = message.direction
        model.timestamp = message.timestamp
        
        self.session.flush()
        
        logger.info(f"✓ ConversationMessage updated (id={message.id})")
        
        return self._to_entity(model)

    def delete(self, message_id: str) -> bool:
        """
        Delete conversation message.
        
        Args:
            message_id: Message ID
            
        Returns:
            True if deleted, False if not found
        """
        model = self.session.query(ConversationMessageModel).filter_by(id=message_id).first()
        
        if not model:
            return False
        
        self.session.delete(model)
        self.session.flush()
        
        logger.info(f"✓ ConversationMessage deleted (id={message_id})")
        
        return True

    def _to_entity(self, model: ConversationMessageModel) -> ConversationMessage:
        """Convert model to entity."""
        return ConversationMessage(
            id=model.id,
            conversation_id=model.conversation_id,
            direction=MessageDirection(model.direction),
            content=model.content,
            timestamp=model.timestamp,
        )
