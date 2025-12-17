"""
Conversation Service - Business logic for conversation management.

Este service orquestra operações de conversação separadas da lógica de IA.
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
    Service para gerenciar conversas (business logic).
    
    Responsabilidades:
    - CRUD de conversas
    - Transições de status
    - Transferências para secretárias
    - Fechamento de conversas
    """

    def __init__(self, db: Session):
        """Inicializar service com sessão do banco."""
        self.db = db

    def get_or_create(
        self,
        chat_id: str,
        phone_number: str,
        name: Optional[str] = None,
    ) -> ConversationModel:
        """
        Buscar conversa existente ou criar nova.
        
        Args:
            chat_id: ID do chat WhatsApp
            phone_number: Número de telefone
            name: Nome do contato (opcional)
            
        Returns:
            Conversação encontrada ou criada
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
        Atualizar status da conversa com validação de transições.
        
        Args:
            conversation_id: ID da conversa
            new_status: Novo status
            
        Returns:
            Conversa atualizada
            
        Raises:
            NotFoundException: Se conversa não existir
            BusinessRuleError: Se transição inválida
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
        Fechar conversa.
        
        Args:
            conversation_id: ID da conversa
            reason: Motivo do fechamento (opcional)
            
        Returns:
            Conversa fechada
            
        Raises:
            NotFoundException: Se conversa não existir
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
        Transferir conversa para secretária.
        
        Args:
            conversation_id: ID da conversa
            user_id: ID do usuário (secretária)
            
        Returns:
            Conversa transferida
            
        Raises:
            NotFoundException: Se conversa não existir
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
        Obter conversas ativas.
        
        Args:
            limit: Número máximo de resultados
            
        Returns:
            Lista de conversas ativas
        """
        from robbot.adapters.repositories.conversation_repository import (
            ConversationRepository
        )
        
        repo = ConversationRepository(self.db)
        return repo.get_active(limit=limit)

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
