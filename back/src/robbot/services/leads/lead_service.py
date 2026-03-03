"""
Lead Service - Business logic for lead management.

This service orchestrates lead operations and status transitions using rich domain entities.
"""

import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.lead_repository import LeadRepository
from robbot.core.custom_exceptions import BusinessRuleError, NotFoundException
from robbot.domain.shared.enums import LeadStatus
from robbot.domain.leads.mapper import LeadMapper
from robbot.domain.leads.lead import Lead
from robbot.infra.persistence.models.lead_model import LeadModel

logger = logging.getLogger(__name__)


class LeadService:
    """
    Service to manage leads (business logic).

    Responsibilities:
    - Lead CRUD operations
    - Status transitions (Domain logic)
    - Assignment to secretaries
    - Lead conversion and loss tracking
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = LeadRepository(db)

    def create_from_conversation(
        self,
        phone_number: str,
        name: str,
        email: str | None = None,
    ) -> LeadModel:
        """Create lead from conversation."""
        existing = self.repo.get_by_phone(phone_number)
        if existing:
            logger.warning("[WARNING] Lead already exists (phone=%s)", phone_number)
            return existing

        # Create rich domain entity
        lead_domain = Lead.create(name=name, phone_number=phone_number)
        lead_domain.email = email

        # Map to model and persist
        lead_model = LeadMapper.to_model(lead_domain)
        created = self.repo.create(lead_model)

        logger.info("[SUCCESS] Lead created (id=%s, phone=%s)", created.id, phone_number)
        return created

    def update_maturity(
        self,
        lead_id: str,
        new_score: int,
    ) -> LeadModel:
        """Update lead maturity score using domain rules."""
        lead_model = self.repo.get_by_id(lead_id)
        if not lead_model:
            raise NotFoundException(f"Lead {lead_id} not found")

        # Domain transition
        lead_domain = LeadMapper.to_domain(lead_model)
        old_score = lead_domain.maturity_score.value
        
        lead_domain.update_score(new_score)
        
        # Save change
        LeadMapper.to_model(lead_domain, lead_model)
        updated = self.repo.update(lead_model)

        logger.info("[SUCCESS] Score updated (lead_id=%s, %s -> %s, status=%s)", 
                    lead_id, old_score, new_score, lead_domain.status)
        return updated

    def assign_to_user(
        self,
        lead_id: str,
        user_id: int,
    ) -> LeadModel:
        """Assign lead to secretary."""
        lead_model = self.repo.get_by_id(lead_id)
        if not lead_model:
            raise NotFoundException(f"Lead {lead_id} not found")

        lead_domain = LeadMapper.to_domain(lead_model)
        lead_domain.assign_to(user_id)
        
        LeadMapper.to_model(lead_domain, lead_model)
        updated = self.repo.update(lead_model)

        logger.info("[SUCCESS] Lead assigned (lead_id=%s, user_id=%s)", lead_id, user_id)
        return updated

    def convert(self, lead_id: str) -> LeadModel:
        """Mark lead as converted/scheduled."""
        lead_model = self.repo.get_by_id(lead_id)
        if not lead_model:
            raise NotFoundException(f"Lead {lead_id} not found")

        lead_domain = LeadMapper.to_domain(lead_model)
        lead_domain.convert()
        
        LeadMapper.to_model(lead_domain, lead_model)
        updated = self.repo.update(lead_model)

        logger.info("[SUCCESS] Lead converted (lead_id=%s)", lead_id)
        return updated

    def mark_lost(
        self,
        lead_id: str,
        reason: str | None = None,
    ) -> LeadModel:
        """Mark lead as lost."""
        lead_model = self.repo.get_by_id(lead_id)
        if not lead_model:
            raise NotFoundException(f"Lead {lead_id} not found")

        lead_domain = LeadMapper.to_domain(lead_model)
        lead_domain.update_score(0)
        
        LeadMapper.to_model(lead_domain, lead_model)
        updated = self.repo.update(lead_model)

        logger.info("[SUCCESS] Lead marked as lost (lead_id=%s, reason=%s)", lead_id, reason)
        return updated

    def soft_delete(self, lead_id: str) -> LeadModel:
        """Soft delete lead."""
        lead_model = self.repo.get_by_id(lead_id)
        if not lead_model:
            raise NotFoundException(f"Lead {lead_id} not found")

        lead_domain = LeadMapper.to_domain(lead_model)
        lead_domain.soft_delete()
        
        LeadMapper.to_model(lead_domain, lead_model)
        updated = self.repo.update(lead_model)

        logger.info("[SUCCESS] Lead soft-deleted (lead_id=%s)", lead_id)
        return updated

    def restore(self, lead_id: str) -> LeadModel:
        """Restore soft-deleted lead."""
        lead_model = self.repo.get_by_id(lead_id)
        if not lead_model:
            raise NotFoundException(f"Lead {lead_id} not found")

        lead_domain = LeadMapper.to_domain(lead_model)
        lead_domain.restore()
        
        LeadMapper.to_model(lead_domain, lead_model)
        updated = self.repo.update(lead_model)

        logger.info("[SUCCESS] Lead restored (lead_id=%s)", lead_id)
        return updated

    def list_leads(
        self,
        status: LeadStatus | None = None,
        phone_number: str | None = None,
        assigned_to_user_id: int | None = None,
        min_score: int | None = None,
        unassigned_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[LeadModel], int]:
        """List leads with multiple filters."""
        # This remains mostly repository-based for performance
        return self.repo.list_leads(
            status=status,
            phone_number=phone_number,
            assigned_to_user_id=assigned_to_user_id,
            min_score=min_score,
            unassigned_only=unassigned_only,
            limit=limit,
            offset=offset
        )

    def auto_assign_lead(self, lead_id: str) -> LeadModel | None:
        """Auto-assign lead to available secretary using round-robin logic."""
        from robbot.infra.persistence.repositories.user_repository import UserRepository

        lead_model = self.repo.get_by_id(lead_id)
        if not lead_model:
            raise NotFoundException(f"Lead {lead_id} not found")

        user_repo = UserRepository(self.db)
        secretaries = [u for u in user_repo.list_all() if u.role == "user"]

        if not secretaries:
            logger.warning("[WARNING] No secretary available for assignment")
            return None

        # Workload balancing
        active_leads = self.repo.get_leads_by_statuses([LeadStatus.ENGAGED, LeadStatus.INTERESTED])
        from collections import Counter
        lead_counts = Counter(l.assigned_to_user_id for l in active_leads if l.assigned_to_user_id)
        
        selected_secretary = min(secretaries, key=lambda s: lead_counts.get(s.id, 0))

        lead_domain = LeadMapper.to_domain(lead_model)
        lead_domain.assign_to(selected_secretary.id)
        
        LeadMapper.to_model(lead_domain, lead_model)
        updated = self.repo.update(lead_model)

        logger.info("[SUCCESS] Lead auto-assigned (lead_id=%s, user_id=%s)", lead_id, selected_secretary.id)
        return updated

