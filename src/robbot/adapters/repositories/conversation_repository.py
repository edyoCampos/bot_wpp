"""Repository for conversation persistence and retrieval operations."""

from typing import Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from robbot.infra.db.models.conversation_model import ConversationModel
from robbot.domain.enums import ConversationStatus, LeadStatus


class ConversationRepository:
    """Data access layer for conversations."""

    def __init__(self, db: Session):
        """Initialize repository with database session.

        Args:
            db: SQLAlchemy session
        """
        self.db = db

    def get_by_id(self, conversation_id: str) -> Optional[ConversationModel]:
        """Get conversation by ID.

        Args:
            conversation_id: Conversation UUID

        Returns:
            Conversation or None if not found
        """
        stmt = select(ConversationModel).where(
            ConversationModel.id == conversation_id
        )
        return self.db.scalars(stmt).first()

    def get_by_chat_id(self, chat_id: str) -> Optional[ConversationModel]:
        """Get conversation by WhatsApp chat ID.

        Args:
            chat_id: WhatsApp chat ID (e.g., '5511999999999@c.us')

        Returns:
            Conversation or None if not found
        """
        stmt = select(ConversationModel).where(
            ConversationModel.chat_id == chat_id
        )
        return self.db.scalars(stmt).first()

    def create(
        self,
        chat_id: str,
        phone_number: str,
        name: Optional[str] = None,
        status: ConversationStatus = ConversationStatus.ACTIVE,
    ) -> ConversationModel:
        """Create new conversation.

        Args:
            chat_id: WhatsApp chat ID
            phone_number: Phone number
            name: Contact name (optional)
            status: Initial status (default: ACTIVE)

        Returns:
            Created conversation
        """
        conversation = ConversationModel(
            chat_id=chat_id,
            phone_number=phone_number,
            name=name,
            status=status,
            last_message_at=datetime.utcnow(),
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def update(
        self,
        conversation_id: str,
        data: dict,
    ) -> ConversationModel:
        """Update conversation.

        Args:
            conversation_id: Conversation UUID
            data: Dictionary with fields to update

        Returns:
            Updated conversation

        Raises:
            ValueError: If conversation not found
        """
        conversation = self.get_by_id(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        for key, value in data.items():
            if hasattr(conversation, key):
                setattr(conversation, key, value)

        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def update_status(
        self,
        conversation_id: str,
        status: ConversationStatus,
    ) -> ConversationModel:
        """Update conversation status.

        Args:
            conversation_id: Conversation UUID
            status: New status

        Returns:
            Updated conversation
        """
        return self.update(conversation_id, {"status": status})

    def update_last_message_at(
        self,
        conversation_id: str,
    ) -> ConversationModel:
        """Update last message timestamp.

        Args:
            conversation_id: Conversation UUID

        Returns:
            Updated conversation
        """
        return self.update(
            conversation_id,
            {"last_message_at": datetime.utcnow()}
        )

    def get_active(self, limit: int = 100) -> list[ConversationModel]:
        """Get active conversations.

        Args:
            limit: Max number of conversations to return

        Returns:
            List of active conversations
        """
        stmt = (
            select(ConversationModel)
            .where(ConversationModel.status == ConversationStatus.ACTIVE)
            .order_by(ConversationModel.last_message_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ConversationModel]:
        """List all conversations with pagination.

        Args:
            skip: Number of records to skip
            limit: Max number of records to return

        Returns:
            List of conversations
        """
        stmt = (
            select(ConversationModel)
            .order_by(ConversationModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_all(self) -> list[ConversationModel]:
        """Get all conversations without pagination.

        Returns:
            List of all conversations
        """
        stmt = select(ConversationModel).order_by(ConversationModel.created_at.desc())
        return list(self.db.scalars(stmt).all())
