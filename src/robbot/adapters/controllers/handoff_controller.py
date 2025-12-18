"""
Handoff endpoints - Gerenciar transição bot→humano.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from robbot.adapters.repositories.conversation_repository import ConversationRepository
from robbot.adapters.repositories.lead_repository import LeadRepository
from robbot.core.security import get_current_user
from robbot.domain.enums import ConversationStatus
from robbot.infra.db.session import get_db
from robbot.services.handoff_service import HandoffService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["Handoff"])


# ============================================================================
# SCHEMAS
# ============================================================================


class TriggerHandoffRequest(BaseModel):
    """Request para disparar handoff."""
    
    reason: str = Field(
        ...,
        description="Motivo do handoff: score_high, bot_confused, manual"
    )
    additional_context: str | None = Field(
        None,
        description="Contexto adicional opcional"
    )


class AssignConversationRequest(BaseModel):
    """Request para atribuir conversa."""
    
    user_id: str = Field(..., description="UUID do atendente")


class HandoffResponse(BaseModel):
    """Response padrão de handoff."""
    
    status: str
    conversation_id: str
    message: str | None = None
    reason: str | None = None


class PendingHandoffConversation(BaseModel):
    """Conversa aguardando handoff."""
    
    conversation_id: str
    phone_number: str
    lead_name: str | None
    maturity_score: int
    escalation_reason: str | None
    is_urgent: bool
    waiting_time_minutes: int
    last_message: str


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/{conversation_id}/handoff", response_model=HandoffResponse)
async def trigger_handoff(
    conversation_id: str,
    request: TriggerHandoffRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Any:
    """
    Disparar handoff bot→humano.
    
    **Motivos válidos:**
    - `score_high`: Lead com score >= 85 (pronto para agendamento)
    - `bot_confused`: Bot não conseguiu entender (3+ intents OUTRO)
    - `manual`: Atendente decidiu assumir manualmente
    
    **Permissões:** Admin ou Agent
    """
    try:
        handoff_service = HandoffService(
            ConversationRepository(db),
            LeadRepository(db)
        )
        
        # Buscar score do lead para passar ao service
        conv_repo = ConversationRepository(db)
        conversation = conv_repo.get_by_id(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        score = conversation.lead.maturity_score if conversation.lead else None
        
        result = await handoff_service.trigger_handoff(
            session=db,
            conversation_id=conversation_id,
            reason=request.reason,
            score=score,
            additional_context=request.additional_context,
        )
        
        logger.info(
            f"✓ Handoff triggered via API: conv={conversation_id}, "
            f"reason={request.reason}, user_id={current_user['user_id']}"
        )
        
        return HandoffResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"✗ Erro ao disparar handoff: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger handoff: {str(e)}"
        )


@router.post("/{conversation_id}/assign", response_model=HandoffResponse)
async def assign_conversation(
    conversation_id: str,
    request: AssignConversationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Any:
    """
    Atribuir conversa para atendente humano.
    
    Conversa passa de PENDING_HANDOFF → ACTIVE_HUMAN.
    Bot silencia e todas as mensagens são direcionadas ao atendente.
    
    **Permissões:** Admin ou Agent
    """
    try:
        handoff_service = HandoffService(
            ConversationRepository(db),
            LeadRepository(db)
        )
        
        conversation = await handoff_service.assign_to_human(
            session=db,
            conversation_id=conversation_id,
            user_id=request.user_id,
        )
        
        logger.info(
            f"✓ Conversation assigned via API: conv={conversation_id}, "
            f"to_user={request.user_id}, by_user_id={current_user['user_id']}"
        )
        
        return HandoffResponse(
            status="assigned",
            conversation_id=conversation_id,
            message=f"Conversa atribuída para {request.user_id}"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"✗ Erro ao atribuir conversa: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign conversation: {str(e)}"
        )


@router.post("/{conversation_id}/complete", response_model=dict)
async def complete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Any:
    """
    Marcar conversa como concluída após agendamento confirmado.
    
    Conversa passa de ACTIVE_HUMAN → COMPLETED.
    Lead é marcado como SCHEDULED com score 100.
    Métricas de conversão são calculadas.
    
    **Permissões:** Apenas o atendente atribuído ou Admin
    """
    try:
        handoff_service = HandoffService(
            ConversationRepository(db),
            LeadRepository(db)
        )
        
        result = await handoff_service.mark_as_completed(
            session=db,
            conversation_id=conversation_id,
            user_id=str(current_user["user_id"]),
        )
        
        logger.info(
            f"✓ Conversation completed via API: conv={conversation_id}, "
            f"user_id={current_user['user_id']}, metrics={result['metrics']}"
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"✗ Erro ao completar conversa: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete conversation: {str(e)}"
        )


@router.post("/{conversation_id}/return-to-bot", response_model=HandoffResponse)
async def return_conversation_to_bot(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Any:
    """
    Devolver conversa ao bot.
    
    Conversa passa de ACTIVE_HUMAN → ACTIVE_BOT.
    Bot volta a responder automaticamente.
    
    **Uso:** Quando atendente percebe que bot consegue resolver.
    
    **Permissões:** Apenas o atendente atribuído ou Admin
    """
    try:
        handoff_service = HandoffService(
            ConversationRepository(db),
            LeadRepository(db)
        )
        
        conversation = await handoff_service.return_to_bot(
            session=db,
            conversation_id=conversation_id,
            user_id=str(current_user["user_id"]),
        )
        
        logger.info(
            f"✓ Conversation returned to bot via API: conv={conversation_id}, "
            f"user_id={current_user['user_id']}"
        )
        
        return HandoffResponse(
            status="returned_to_bot",
            conversation_id=conversation_id,
            message="Conversa devolvida ao bot"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"✗ Erro ao devolver conversa: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to return conversation: {str(e)}"
        )


@router.get("/pending-handoff", response_model=list[PendingHandoffConversation])
async def get_pending_handoffs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Any:
    """
    Listar conversas aguardando handoff.
    
    Retorna todas as conversas em status PENDING_HANDOFF,
    ordenadas por:
    1. Urgência (is_urgent=true primeiro)
    2. Score (maior primeiro)
    3. Tempo aguardando (mais antigo primeiro)
    
    **Permissões:** Admin ou Agent
    """
    try:
        from datetime import datetime, timezone
        from robbot.adapters.repositories.conversation_message_repository import (
            ConversationMessageRepository
        )
        
        conv_repo = ConversationRepository(db)
        msg_repo = ConversationMessageRepository(db)
        
        # Buscar conversas pendentes
        conversations = conv_repo.get_by_status(ConversationStatus.PENDING_HANDOFF)
        
        result = []
        
        for conv in conversations:
            # Calcular tempo aguardando
            waiting_time = datetime.now(timezone.utc) - conv.updated_at
            waiting_minutes = int(waiting_time.total_seconds() / 60)
            
            # Buscar última mensagem
            messages = msg_repo.get_by_conversation_id(conv.id, limit=1)
            last_message = messages[0].content if messages else "N/A"
            
            result.append(
                PendingHandoffConversation(
                    conversation_id=conv.id,
                    phone_number=conv.phone_number,
                    lead_name=conv.lead.name if conv.lead else None,
                    maturity_score=conv.lead.maturity_score if conv.lead else 0,
                    escalation_reason=conv.escalation_reason,
                    is_urgent=conv.is_urgent,
                    waiting_time_minutes=waiting_minutes,
                    last_message=last_message[:100],
                )
            )
        
        # Ordenar: urgentes primeiro, depois score, depois tempo
        result.sort(
            key=lambda x: (
                -int(x.is_urgent),  # Urgentes primeiro (- inverte)
                -x.maturity_score,  # Score maior primeiro
                -x.waiting_time_minutes,  # Mais antigo primeiro
            )
        )
        
        logger.info(
            f"✓ Pending handoffs retrieved: {len(result)} conversas, "
            f"user_id={current_user['user_id']}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"✗ Erro ao buscar pending handoffs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending handoffs: {str(e)}"
        )
