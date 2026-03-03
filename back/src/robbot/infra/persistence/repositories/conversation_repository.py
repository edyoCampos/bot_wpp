"""Repository for conversation persistence and retrieval operations."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from robbot.infra.persistence.repositories.base_repository import BaseRepository
from robbot.domain.shared.enums import ConversationStatus
from robbot.infra.persistence.models.conversation_model import ConversationModel
from robbot.infra.persistence.models.lead_model import LeadModel


class ConversationRepository(BaseRepository[ConversationModel]):
    """Data access layer for conversations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        super().__init__(db, ConversationModel)

    def get_by_chat_id(self, chat_id: str) -> ConversationModel | None:
        """Get conversation by WhatsApp chat ID."""
        stmt = (
            select(ConversationModel)
            .options(joinedload(ConversationModel.lead))
            .where(ConversationModel.chat_id == chat_id)
        )
        return self.db.scalars(stmt).first()

    def get_by_id(self, id: str) -> ConversationModel | None:  # Corrected type hint to str (UUID)
        """Get conversation by ID with lead loaded."""
        stmt = (
            select(ConversationModel)
            .options(joinedload(ConversationModel.lead))
            .where(ConversationModel.id == id)
        )
        return self.db.scalars(stmt).first()

    def update_status(
        self,
        conversation_id: str,
        status: ConversationStatus,
    ) -> ConversationModel:
        """Update conversation status."""
        conversation = self.get_by_id(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        conversation.status = status
        conversation.updated_at = datetime.now(UTC)
        self.db.flush()
        self.db.refresh(conversation)
        return conversation

    def get_active(self, limit: int = 100) -> list[ConversationModel]:
        """Get active conversations."""
        stmt = (
            select(ConversationModel)
            .where(ConversationModel.status == ConversationStatus.ACTIVE_BOT)
            .order_by(ConversationModel.last_message_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def find_by_criteria(
        self,
        filters: dict,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ConversationModel]:
        """Find conversations by dynamic criteria."""
        stmt = select(ConversationModel).options(joinedload(ConversationModel.lead))

        # Apply filters dynamically
        if "status" in filters and filters["status"]:
            stmt = stmt.where(ConversationModel.status == filters["status"])

        if "phone_number" in filters and filters["phone_number"]:
            stmt = stmt.where(ConversationModel.phone_number == filters["phone_number"])

        if "is_urgent" in filters and filters["is_urgent"] is not None:
            stmt = stmt.where(ConversationModel.is_urgent == filters["is_urgent"])

        if "assigned_to_user_id" in filters and filters["assigned_to_user_id"]:
            stmt = stmt.join(LeadModel, ConversationModel.id == LeadModel.conversation_id)
            stmt = stmt.where(LeadModel.assigned_to_user_id == filters["assigned_to_user_id"])

        if "conversation_ids" in filters and filters["conversation_ids"] is not None:
            conversation_ids = filters["conversation_ids"]
            stmt = stmt.where(ConversationModel.id.in_(conversation_ids))

        # Order and paginate
        stmt = stmt.order_by(ConversationModel.updated_at.desc()).limit(limit).offset(offset)

        return list(self.db.scalars(stmt).all())

