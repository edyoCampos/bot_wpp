"""Repository for Lead entity."""

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from robbot.infra.persistence.repositories.base_repository import BaseRepository
from robbot.infra.persistence.models.lead_model import LeadModel
from robbot.domain.shared.enums import LeadStatus


class LeadRepository(BaseRepository[LeadModel]):
    """Repository for leads CRUD operations."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        super().__init__(session, LeadModel)

    def get_by_phone(self, phone_number: str) -> LeadModel | None:
        """Get lead by phone number."""
        return self.session.query(LeadModel).filter_by(phone_number=phone_number).first()

    def get_leads_by_statuses(self, statuses: list[LeadStatus]) -> list[LeadModel]:
        """Get leads by a list of statuses."""
        return self.session.query(LeadModel).filter(LeadModel.status.in_(statuses)).all()

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
        """
        List leads with multiple filters and total count.
        """
        query = self.session.query(LeadModel)

        if status:
            query = query.filter(LeadModel.status == status)
        if phone_number:
            query = query.filter(LeadModel.phone_number.ilike(f"%{phone_number}%"))
        if unassigned_only:
            query = query.filter(LeadModel.assigned_to_user_id.is_(None))
        elif assigned_to_user_id is not None:
            query = query.filter(LeadModel.assigned_to_user_id == assigned_to_user_id)
        if min_score is not None:
            query = query.filter(LeadModel.maturity_score >= min_score)

        # Count total
        total = query.count()

        # Apply pagination
        leads = query.offset(offset).limit(limit).all()

        return leads, total

