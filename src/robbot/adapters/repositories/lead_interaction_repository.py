"""Repository for LeadInteraction entity."""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from robbot.domain.entities.lead_interaction import LeadInteraction
from robbot.domain.enums import InteractionType
from robbot.infra.db.models.lead_interaction_model import LeadInteractionModel

logger = logging.getLogger(__name__)


class LeadInteractionRepository:
    """Repository for lead interactions CRUD operations."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        self.session = session

    def create(self, interaction: LeadInteraction) -> LeadInteraction:
        """
        Create new lead interaction.
        
        Args:
            interaction: LeadInteraction entity
            
        Returns:
            Created entity with ID
        """
        model = LeadInteractionModel(
            id=interaction.id,
            lead_id=interaction.lead_id,
            interaction_type=interaction.interaction_type,
            notes=interaction.notes,
            timestamp=interaction.timestamp or datetime.now(timezone.utc),
        )
        
        self.session.add(model)
        self.session.flush()
        
        logger.info(f"✓ LeadInteraction created (id={model.id})")
        
        return self._to_entity(model)

    def get_by_id(self, interaction_id: str) -> Optional[LeadInteraction]:
        """
        Get lead interaction by ID.
        
        Args:
            interaction_id: Interaction ID
            
        Returns:
            LeadInteraction or None
        """
        model = self.session.query(LeadInteractionModel).filter_by(id=interaction_id).first()
        
        if model:
            return self._to_entity(model)
        
        return None

    def get_by_lead(
        self,
        lead_id: str,
        limit: int = 50
    ) -> list[LeadInteraction]:
        """
        Get interactions by lead ID.
        
        Args:
            lead_id: Lead ID
            limit: Maximum number of interactions
            
        Returns:
            List of interactions ordered by timestamp
        """
        models = (
            self.session.query(LeadInteractionModel)
            .filter_by(lead_id=lead_id)
            .order_by(LeadInteractionModel.timestamp.desc())
            .limit(limit)
            .all()
        )
        
        return [self._to_entity(m) for m in models]

    def get_all(self) -> list[LeadInteraction]:
        """
        Get all lead interactions.
        
        Returns:
            List of all interactions
        """
        models = self.session.query(LeadInteractionModel).all()
        return [self._to_entity(m) for m in models]

    def update(self, interaction: LeadInteraction) -> LeadInteraction:
        """
        Update existing lead interaction.
        
        Args:
            interaction: LeadInteraction entity
            
        Returns:
            Updated entity
        """
        model = self.session.query(LeadInteractionModel).filter_by(id=interaction.id).first()
        
        if not model:
            raise ValueError(f"LeadInteraction {interaction.id} not found")
        
        model.interaction_type = interaction.interaction_type
        model.notes = interaction.notes
        model.timestamp = interaction.timestamp
        
        self.session.flush()
        
        logger.info(f"✓ LeadInteraction updated (id={interaction.id})")
        
        return self._to_entity(model)

    def delete(self, interaction_id: str) -> bool:
        """
        Delete lead interaction.
        
        Args:
            interaction_id: Interaction ID
            
        Returns:
            True if deleted, False if not found
        """
        model = self.session.query(LeadInteractionModel).filter_by(id=interaction_id).first()
        
        if not model:
            return False
        
        self.session.delete(model)
        self.session.flush()
        
        logger.info(f"✓ LeadInteraction deleted (id={interaction_id})")
        
        return True

    def _to_entity(self, model: LeadInteractionModel) -> LeadInteraction:
        """Convert model to entity."""
        return LeadInteraction(
            id=model.id,
            lead_id=model.lead_id,
            interaction_type=InteractionType(model.interaction_type),
            notes=model.notes,
            timestamp=model.timestamp,
        )
