"""Repository for Lead entity."""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from robbot.domain.entities.lead import Lead
from robbot.infra.db.models.lead_model import LeadModel

logger = logging.getLogger(__name__)


class LeadRepository:
    """Repository for leads CRUD operations."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        self.session = session

    def create(self, lead: Lead) -> Lead:
        """
        Create new lead.
        
        Args:
            lead: Lead entity
            
        Returns:
            Created entity with ID
        """
        model = LeadModel(
            id=lead.id,
            phone_number=lead.phone_number,
            name=lead.name,
            email=lead.email,
            maturity_score=lead.maturity_score,
            assigned_to_user_id=lead.assigned_to_user_id,
            created_at=lead.created_at,
            updated_at=lead.updated_at,
        )
        
        self.session.add(model)
        self.session.flush()
        
        logger.info(f"✓ Lead created (id={model.id})")
        
        return self._to_entity(model)

    def get_by_id(self, lead_id: str) -> Optional[Lead]:
        """
        Get lead by ID.
        
        Args:
            lead_id: Lead ID
            
        Returns:
            Lead or None
        """
        model = self.session.query(LeadModel).filter_by(id=lead_id).first()
        
        if model:
            return self._to_entity(model)
        
        return None

    def get_by_phone(self, phone_number: str) -> Optional[Lead]:
        """
        Get lead by phone number.
        
        Args:
            phone_number: Phone number
            
        Returns:
            Lead or None
        """
        model = self.session.query(LeadModel).filter_by(phone_number=phone_number).first()
        
        if model:
            return self._to_entity(model)
        
        return None

    def get_all(self) -> list[Lead]:
        """
        Get all leads.
        
        Returns:
            List of all leads
        """
        models = self.session.query(LeadModel).all()
        return [self._to_entity(m) for m in models]

    def update(self, lead: Lead) -> Lead:
        """
        Update existing lead.
        
        Args:
            lead: Lead entity
            
        Returns:
            Updated entity
        """
        model = self.session.query(LeadModel).filter_by(id=lead.id).first()
        
        if not model:
            raise ValueError(f"Lead {lead.id} not found")
        
        model.phone_number = lead.phone_number
        model.name = lead.name
        model.email = lead.email
        model.maturity_score = lead.maturity_score
        model.assigned_to_user_id = lead.assigned_to_user_id
        model.updated_at = datetime.now(timezone.utc)
        
        self.session.flush()
        
        logger.info(f"✓ Lead updated (id={lead.id})")
        
        return self._to_entity(model)

    def delete(self, lead_id: str) -> bool:
        """
        Delete lead.
        
        Args:
            lead_id: Lead ID
            
        Returns:
            True if deleted, False if not found
        """
        model = self.session.query(LeadModel).filter_by(id=lead_id).first()
        
        if not model:
            return False
        
        self.session.delete(model)
        self.session.flush()
        
        logger.info(f"✓ Lead deleted (id={lead_id})")
        
        return True

    def _to_entity(self, model: LeadModel) -> Lead:
        """Convert model to entity."""
        return Lead(
            id=model.id,
            phone_number=model.phone_number,
            name=model.name,
            email=model.email,
            maturity_score=model.maturity_score,
            assigned_to_user_id=model.assigned_to_user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
