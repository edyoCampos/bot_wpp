"""
Lead Service - Business logic for lead management.

This service orchestrates lead operations and status transitions.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from robbot.adapters.repositories.lead_repository import LeadRepository
from robbot.core.exceptions import BusinessRuleError, NotFoundException
from robbot.domain.entities.lead import Lead
from robbot.domain.enums import LeadStatus

logger = logging.getLogger(__name__)


class LeadService:
    """
    Service to manage leads (business logic).
    
    Responsibilities:
    - Lead CRUD operations
    - Status transitions
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
        email: Optional[str] = None,
    ) -> Lead:
        """
        Create lead from conversation.
        
        Args:
            phone_number: Phone number
            name: Lead name
            email: Email (optional)
            
        Returns:
            Created lead
        """
        existing = self.repo.get_by_phone(phone_number)
        if existing:
            logger.warning(f"Lead já existe (phone={phone_number})")
            return existing
        
        lead = Lead(
            phone_number=phone_number,
            name=name,
            email=email,
            maturity_score=0,
        )
        
        created = self.repo.create(lead)
        
        logger.info(f"✓ Lead criado (id={created.id}, phone={phone_number})")
        
        return created

    def update_maturity(
        self,
        lead_id: str,
        new_score: int,
    ) -> Lead:
        """
        Update lead maturity score.
        
        Args:
            lead_id: Lead ID
            new_score: New score (0-100)
            
        Returns:
            Updated lead
            
        Raises:
            NotFoundException: If lead not found
            BusinessRuleError: If score is invalid
        """
        if not 0 <= new_score <= 100:
            raise BusinessRuleError("Maturity score must be between 0 and 100")
        
        lead = self.repo.get_by_id(lead_id)
        if not lead:
            raise NotFoundException(f"Lead {lead_id} not found")
        
        old_score = lead.maturity_score
        lead.maturity_score = new_score
        
        updated = self.repo.update(lead)
        
        logger.info(
            f"✓ Score atualizado (lead_id={lead_id}, {old_score} → {new_score})"
        )
        
        return updated

    def assign_to_user(
        self,
        lead_id: str,
        user_id: int,
    ) -> Lead:
        """
        Atribuir lead para secretária.
        
        Args:
            lead_id: ID do lead
            user_id: ID do usuário
            
        Returns:
            Lead atualizado
            
        Raises:
            NotFoundException: Se lead não existir
        """
        lead = self.repo.get_by_id(lead_id)
        if not lead:
            raise NotFoundException(f"Lead {lead_id} not found")
        
        lead.assigned_to_user_id = user_id
        updated = self.repo.update(lead)
        
        logger.info(f"✓ Lead atribuído (lead_id={lead_id}, user_id={user_id})")
        
        return updated

    def convert(self, lead_id: str) -> Lead:
        """
        Marcar lead como convertido.
        
        Args:
            lead_id: ID do lead
            
        Returns:
            Lead atualizado
            
        Raises:
            NotFoundException: Se lead não existir
        """
        lead = self.repo.get_by_id(lead_id)
        if not lead:
            raise NotFoundException(f"Lead {lead_id} not found")
        
        lead.maturity_score = 100
        updated = self.repo.update(lead)
        
        logger.info(f"✓ Lead convertido (lead_id={lead_id})")
        
        return updated

    def mark_lost(
        self,
        lead_id: str,
        reason: Optional[str] = None,
    ) -> Lead:
        """
        Marcar lead como perdido.
        
        Args:
            lead_id: ID do lead
            reason: Motivo da perda (opcional)
            
        Returns:
            Lead atualizado
            
        Raises:
            NotFoundException: Se lead não existir
        """
        lead = self.repo.get_by_id(lead_id)
        if not lead:
            raise NotFoundException(f"Lead {lead_id} not found")
        
        lead.maturity_score = 0
        updated = self.repo.update(lead)
        
        logger.info(f"✓ Lead marcado como perdido (lead_id={lead_id}, reason={reason})")
        
        return updated

    def get_leads_by_status(
        self,
        status: LeadStatus,
        limit: int = 50,
    ) -> list[Lead]:
        """
        Get leads by status.
        
        Args:
            status: Lead status
            limit: Maximum number of results
            
        Returns:
            List of leads
        """
        # Buscar todos os leads e filtrar por status
        all_leads = self.repo.get_all()
        
        # Filtrar por status se fornecido
        if status:
            all_leads = [lead for lead in all_leads if lead.status == status]
        
        return all_leads[:limit]

    def get_unassigned_leads(self, limit: int = 50) -> list[Lead]:
        """
        Get unassigned leads.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of leads without assignment
        """
        all_leads = self.repo.get_all()
        
        # Filter unassigned
        unassigned = [
            lead for lead in all_leads
            if lead.assigned_to_user_id is None
        ]
        
        return unassigned[:limit]
    
    def list_leads(
        self,
        status: Optional[LeadStatus] = None,
        assigned_to_user_id: Optional[int] = None,
        min_score: Optional[int] = None,
        unassigned_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Lead], int]:
        """
        List leads with multiple filters.
        
        Args:
            status: Filter by lead status
            assigned_to_user_id: Filter by assigned user
            min_score: Minimum maturity score
            unassigned_only: Show only unassigned leads
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            Tuple of (leads list, total count)
        """
        all_leads = self.repo.get_all()
        
        # Apply filters
        filtered = all_leads
        
        if status:
            filtered = [l for l in filtered if l.status == status]
        
        if unassigned_only:
            filtered = [l for l in filtered if l.assigned_to_user_id is None]
        elif assigned_to_user_id is not None:
            filtered = [l for l in filtered if l.assigned_to_user_id == assigned_to_user_id]
        
        if min_score is not None:
            filtered = [l for l in filtered if l.maturity_score >= min_score]
        
        total = len(filtered)
        paginated = filtered[offset:offset + limit]
        
        return paginated, total

    def auto_assign_lead(self, lead_id: str) -> Optional[Lead]:
        """
        Atribuir lead automaticamente para secretária disponível.
        
        Implementa lógica de round-robin baseada em carga de trabalho.
        
        Args:
            lead_id: ID do lead
            
        Returns:
            Lead atualizado ou None se nenhuma secretária disponível
        """
        from robbot.adapters.repositories.user_repository import UserRepository
        
        lead = self.repo.get_by_id(lead_id)
        if not lead:
            raise NotFoundException(f"Lead {lead_id} not found")
        
        # Buscar secretárias ativas
        user_repo = UserRepository(self.db)
        all_users = user_repo.get_all()
        
        # Filtrar secretárias (role=user e ativas)
        secretaries = [u for u in all_users if u.role == "user"]
        
        if not secretaries:
            logger.warning("Nenhuma secretária disponível para atribuição")
            return None
        
        # Balanceamento de carga: atribuir para secretária com menos leads ativos
        from collections import Counter
        active_leads = [l for l in self.repo.get_all() if l.assigned_to_user_id and l.status in [LeadStatus.ENGAGED, LeadStatus.INTERESTED]]
        lead_counts = Counter(l.assigned_to_user_id for l in active_leads)
        selected_secretary = min(secretaries, key=lambda s: lead_counts.get(s.id, 0))
        
        lead.assigned_to_user_id = selected_secretary.id
        updated = self.repo.update(lead)
        
        logger.info(
            f"✓ Lead auto-atribuído (lead_id={lead_id}, "
            f"user_id={selected_secretary.id})"
        )
        
        return updated

    def soft_delete(self, lead_id: str) -> Lead:
        """
        Soft delete de lead (marca deleted_at).
        
        Args:
            lead_id: ID do lead
            
        Returns:
            Lead marcado como deletado
            
        Raises:
            NotFoundException: Se lead não existir
        """
        lead = self.repo.get_by_id(lead_id)
        if not lead:
            raise NotFoundException(f"Lead {lead_id} not found")
        
        if lead.deleted_at:
            logger.warning(f"Lead já estava deletado (lead_id={lead_id})")
            return lead
        
        lead.deleted_at = datetime.now(timezone.utc)
        updated = self.repo.update(lead)
        
        logger.info(f"✓ Lead soft-deleted (lead_id={lead_id})")
        
        return updated

    def restore(self, lead_id: str) -> Lead:
        """
        Restaurar lead soft-deleted.
        
        Args:
            lead_id: ID do lead
            
        Returns:
            Lead restaurado
            
        Raises:
            NotFoundException: Se lead não existir
        """
        # Buscar sem filtrar deleted_at
        lead = self.repo.get_by_id(lead_id)
        if not lead:
            raise NotFoundException(f"Lead {lead_id} not found")
        
        if not lead.deleted_at:
            logger.warning(f"Lead não estava deletado (lead_id={lead_id})")
            return lead
        
        lead.deleted_at = None
        updated = self.repo.update(lead)
        
        logger.info(f"✓ Lead restaurado (lead_id={lead_id})")
        
        return updated
