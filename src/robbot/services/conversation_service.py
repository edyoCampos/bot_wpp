"""
Conversation Service - Business logic for conversation management.

This service orchestrates conversation operations separate from AI logic.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from robbot.core.exceptions import BusinessRuleError, NotFoundException
from robbot.domain.enums import ConversationStatus, LeadStatus
from robbot.infra.db.models.conversation_model import ConversationModel

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Service to manage conversations (business logic).
    
    Responsibilities:
    - Conversation CRUD operations
    - Status transitions
    - Transfers to secretaries
    - Conversation closure
    """

    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db

    def get_or_create(
        self,
        chat_id: str,
        phone_number: str,
        name: Optional[str] = None,
    ) -> ConversationModel:
        """
        Get existing conversation or create new one.
        
        Args:
            chat_id: WhatsApp chat ID
            phone_number: Phone number
            name: Contact name (optional)
            
        Returns:
            Found or created conversation
        """
        from robbot.adapters.repositories.conversation_repository import (
            ConversationRepository
        )
        
        repo = ConversationRepository(self.db)
        
        # Tentar buscar existente
        conversation = repo.get_by_chat_id(chat_id)
        
        if conversation:
            logger.info(f"✓ Conversa encontrada (id={conversation.id})")
            return conversation
        
        # Criar nova conversa
        conversation = repo.create(
            chat_id=chat_id,
            phone_number=phone_number,
            name=name,
            status=ConversationStatus.ACTIVE,
        )
        
        logger.info(f"✓ Nova conversa criada (id={conversation.id})")
        
        return conversation

    def update_status(
        self,
        conversation_id: str,
        new_status: ConversationStatus,
    ) -> ConversationModel:
        """
        Update conversation status with transition validation.
        
        Args:
            conversation_id: Conversation ID
            new_status: New status
            
        Returns:
            Updated conversation
            
        Raises:
            NotFoundException: If conversation not found
            BusinessRuleError: If transition is invalid
        """
        from robbot.adapters.repositories.conversation_repository import (
            ConversationRepository
        )
        
        repo = ConversationRepository(self.db)
        conversation = repo.get_by_id(conversation_id)
        
        if not conversation:
            raise NotFoundException(f"Conversation {conversation_id} not found")
        
        old_status = conversation.status
        
        # Validar transição de status
        if not self._is_valid_transition(old_status, new_status):
            raise BusinessRuleError(
                f"Invalid status transition: {old_status} -> {new_status}"
            )
        
        # Atualizar status
        conversation = repo.update_status(conversation_id, new_status)
        
        logger.info(
            f"✓ Status atualizado (conv_id={conversation_id}, "
            f"{old_status} → {new_status})"
        )
        
        return conversation

    def close(self, conversation_id: str, reason: Optional[str] = None) -> ConversationModel:
        """
        Close conversation.
        
        Args:
            conversation_id: Conversation ID
            reason: Closure reason (optional)
            
        Returns:
            Closed conversation
            
        Raises:
            NotFoundException: If conversation not found
        """
        from robbot.adapters.repositories.conversation_repository import (
            ConversationRepository
        )
        
        repo = ConversationRepository(self.db)
        conversation = repo.get_by_id(conversation_id)
        
        if not conversation:
            raise NotFoundException(f"Conversation {conversation_id} not found")
        
        # Atualizar para CLOSED
        conversation = repo.update(conversation_id, {
            "status": ConversationStatus.CLOSED,
            "closed_at": datetime.now(timezone.utc),
        })
        
        logger.info(
            f"✓ Conversa fechada (id={conversation_id}, reason={reason})"
        )
        
        return conversation

    def transfer_to_secretary(
        self,
        conversation_id: str,
        user_id: int,
    ) -> ConversationModel:
        """
        Transfer conversation to secretary.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID (secretary)
            
        Returns:
            Transferred conversation
            
        Raises:
            NotFoundException: If conversation not found
        """
        from robbot.adapters.repositories.conversation_repository import (
            ConversationRepository
        )
        
        repo = ConversationRepository(self.db)
        conversation = repo.get_by_id(conversation_id)
        
        if not conversation:
            raise NotFoundException(f"Conversation {conversation_id} not found")
        
        # Atualizar status e atribuir
        conversation = repo.update(conversation_id, {
            "status": ConversationStatus.TRANSFERRED,
            "assigned_to_user_id": user_id,
        })
        
        logger.info(
            f"✓ Conversa transferida (id={conversation_id}, user_id={user_id})"
        )
        
        return conversation

    def get_active_conversations(self, limit: int = 100) -> list[ConversationModel]:
        """
        Get active conversations.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of active conversations
        """
        from robbot.adapters.repositories.conversation_repository import (
            ConversationRepository
        )
        
        repo = ConversationRepository(self.db)
        return repo.get_active(limit=limit)
    
    def list_conversations(
        self,
        status: Optional[ConversationStatus] = None,
        is_urgent: Optional[bool] = None,
        assigned_to_user_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[ConversationModel], int]:
        """
        List conversations with filters.
        
        Args:
            status: Filter by conversation status
            is_urgent: Filter by urgency flag
            assigned_to_user_id: Filter by assigned user
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            Tuple of (conversations list, total count)
        """
        from robbot.adapters.repositories.conversation_repository import (
            ConversationRepository
        )
        
        repo = ConversationRepository(self.db)
        
        filters = {}
        if status is not None:
            filters["status"] = status
        if is_urgent is not None:
            filters["is_urgent"] = is_urgent
        if assigned_to_user_id is not None:
            filters["assigned_to_user_id"] = assigned_to_user_id
        
        conversations = repo.find_by_criteria(filters, limit=limit, offset=offset)
        total = len(repo.find_by_criteria(filters))
        
        return conversations, total
    
    def get_by_id(self, conversation_id: str) -> Optional[ConversationModel]:
        """
        Get conversation by ID.
        
        Args:
            conversation_id: UUID of the conversation
            
        Returns:
            Conversation model or None if not found
        """
        from robbot.adapters.repositories.conversation_repository import (
            ConversationRepository
        )
        
        repo = ConversationRepository(self.db)
        return repo.get_by_id(conversation_id)

    def _is_valid_transition(
        self,
        old_status: ConversationStatus,
        new_status: ConversationStatus,
    ) -> bool:
        """
        Validar se transição de status é permitida.
        
        Args:
            old_status: Status atual
            new_status: Status desejado
            
        Returns:
            True se transição válida
        """
        # Mapa de transições válidas
        valid_transitions = {
            ConversationStatus.ACTIVE: [
                ConversationStatus.WAITING_SECRETARY,
                ConversationStatus.TRANSFERRED,
                ConversationStatus.CLOSED,
            ],
            ConversationStatus.WAITING_SECRETARY: [
                ConversationStatus.ACTIVE,
                ConversationStatus.TRANSFERRED,
                ConversationStatus.CLOSED,
            ],
            ConversationStatus.TRANSFERRED: [
                ConversationStatus.ACTIVE,
                ConversationStatus.CLOSED,
            ],
            ConversationStatus.CLOSED: [
                # Uma vez fechada, pode reabrir
                ConversationStatus.ACTIVE,
            ],
        }
        
        allowed = valid_transitions.get(old_status, [])
        return new_status in allowed

    def update_notes(
        self,
        conversation_id: str,
        notes: str,
    ) -> ConversationModel:
        """
        Update conversation notes.
        
        Args:
            conversation_id: Conversation ID
            notes: Notes text (max 5000 chars)
            
        Returns:
            Updated conversation
            
        Raises:
            NotFoundException: If conversation not found
        """
        from robbot.adapters.repositories.conversation_repository import (
            ConversationRepository
        )
        
        repo = ConversationRepository(self.db)
        conversation = repo.get_by_id(conversation_id)
        
        if not conversation:
            raise NotFoundException(f"Conversation {conversation_id} not found")
        
        updated = repo.update(
            conversation_id=conversation_id,
            data={"notes": notes}
        )
        
        logger.info(f"✓ Notes updated (conv_id={conversation_id})")
        
        return updated

    def find_by_criteria(
        self,
        filters: dict,
    ) -> list[ConversationModel]:
        """
        Find conversations by criteria.
        
        Args:
            filters: Dict with filter criteria (status, assigned_to_user_id, etc.)
            
        Returns:
            List of conversations matching criteria
        """
        from robbot.adapters.repositories.conversation_repository import (
            ConversationRepository
        )
        
        repo = ConversationRepository(self.db)
        return repo.find_by_criteria(filters)
