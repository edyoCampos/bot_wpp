"""Repository for LLMInteraction entity."""

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.base_repository import BaseRepository
from robbot.infra.persistence.models.llm_interaction_model import LLMInteractionModel


class LLMInteractionRepository(BaseRepository[LLMInteractionModel]):
    """Repository for LLM interactions CRUD operations."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        super().__init__(session, LLMInteractionModel)

    def get_by_conversation_id(self, conversation_id: str, limit: int = 50) -> list[LLMInteractionModel]:
        """
        Get interactions by conversation ID.

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of interactions

        Returns:
            List of LLMInteractionModels ordered by created_at
        """
        return (
            self.session.query(LLMInteractionModel)
            .filter_by(conversation_id=conversation_id)
            .order_by(LLMInteractionModel.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_user_id(self, user_id: int, limit: int = 50) -> list[LLMInteractionModel]:
        """
        Get interactions by user ID.

        Args:
            user_id: User ID
            limit: Maximum number of interactions

        Returns:
            List of LLMInteractionModels ordered by created_at
        """
        return (
            self.session.query(LLMInteractionModel)
            .filter_by(user_id=user_id)
            .order_by(LLMInteractionModel.created_at.desc())
            .limit(limit)
            .all()
        )

