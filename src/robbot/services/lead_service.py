"""
Lead Service - Business logic for lead management.

Este service orquestra operações de leads e transições de status.
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
    Service para gerenciar leads (business logic).
    
    Responsabilidades:
    - CRUD de leads
    - Transições de status
    - Atribuição para secretárias
    - Conversão e perda de leads
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
        Criar lead a partir de conversa.
        
        Args:
            phone_number: Número de telefone
            name: Nome do lead
            email: Email (opcional)
            
        Returns:
            Lead criado
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
        Atualizar score de maturidade do lead.
        
        Args:
            lead_id: ID do lead
            new_score: Novo score (0-100)
            
        Returns:
            Lead atualizado
            
        Raises:
            NotFoundException: Se lead não existir
            BusinessRuleError: Se score inválido
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
        Obter leads por status.
        
        Args:
            status: Status dos leads
            limit: Número máximo de resultados
            
        Returns:
            Lista de leads
        """
        # Buscar todos os leads e filtrar por status
        all_leads = self.repo.get_all()
        
        # Filtrar por status se fornecido
        if status:
            all_leads = [lead for lead in all_leads if lead.status == status]
        
        return all_leads[:limit]

    def get_unassigned_leads(self, limit: int = 50) -> list[Lead]:
        """
        Obter leads não atribuídos.
        
        Args:
            limit: Número máximo de resultados
            
        Returns:
            Lista de leads sem atribuição
        """
        all_leads = self.repo.get_all()
        
        # Filtrar não atribuídos
        unassigned = [
            lead for lead in all_leads
            if lead.assigned_to_user_id is None
        ]
        
        return unassigned[:limit]

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
