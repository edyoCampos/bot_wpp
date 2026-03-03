"""Repository for LeadInteraction entity."""

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.base_repository import BaseRepository
from robbot.infra.persistence.models.lead_interaction_model import LeadInteractionModel


class LeadInteractionRepository(BaseRepository[LeadInteractionModel]):
    """Repository for lead interactions CRUD operations."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        super().__init__(session, LeadInteractionModel)

    def get_by_lead_id(self, lead_id: str, limit: int = 50) -> list[LeadInteractionModel]:
        """
        Get interactions by lead ID.

        Args:
            lead_id: Lead ID
            limit: Maximum number of interactions

        Returns:
            List of LeadInteractionModels ordered by timestamp
        """
        return (
            self.session.query(LeadInteractionModel)
            .filter_by(lead_id=lead_id)
            .order_by(LeadInteractionModel.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_by_user_id(self, user_id: int, limit: int = 50) -> list[LeadInteractionModel]:
        """
        Get interactions by user ID.

        Args:
            user_id: User ID
            limit: Maximum number of interactions

        Returns:
            List of LeadInteractionModels ordered by timestamp
        """
        return (
            self.session.query(LeadInteractionModel)
            .filter_by(user_id=user_id)
            .order_by(LeadInteractionModel.timestamp.desc())
            .limit(limit)
            .all()
        )

