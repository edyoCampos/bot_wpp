"""
AI endpoints para conversação e análise.

Este módulo expõe endpoints REST para:
- Processar mensagens via API
- Obter estatísticas de IA
- Gerenciar contextos
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from robbot.services.conversation_orchestrator import get_conversation_orchestrator

router = APIRouter(prefix="/ai", tags=["AI"])


# ========== SCHEMAS ==========

class ProcessMessageRequest(BaseModel):
    """Request para processar mensagem."""
    
    chat_id: str = Field(..., description="ID do chat")
    phone_number: str = Field(..., description="Número do telefone")
    message_text: str = Field(..., description="Texto da mensagem")
    session_name: str = Field(default="default", description="Nome da sessão WAHA")


class ProcessMessageResponse(BaseModel):
    """Response de processamento de mensagem."""
    
    conversation_id: str
    response_sent: bool
    response_text: str
    intent: str
    maturity_score: int


class AIStatsResponse(BaseModel):
    """Response de estatísticas de IA."""
    
    total_conversations: int
    total_llm_interactions: int
    total_tokens_used: int
    average_latency_ms: float
    chromadb_documents: int


# ========== ENDPOINTS ==========

@router.post(
    "/process-message",
    response_model=ProcessMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Processar mensagem e gerar resposta",
    description="""
    Processa mensagem inbound e gera resposta usando Gemini AI.
    
    Fluxo completo:
    1. Busca ou cria conversa
    2. Salva mensagem inbound
    3. Busca contexto do ChromaDB
    4. Detecta intenção
    5. Gera resposta com Gemini
    6. Atualiza score de maturidade
    7. Envia resposta via WAHA
    8. Salva tudo no banco
    """,
)
async def process_message(request: ProcessMessageRequest) -> ProcessMessageResponse:
    """
    Processar mensagem e gerar resposta automática.
    
    Args:
        request: Dados da mensagem
        
    Returns:
        Resultado do processamento
        
    Raises:
        HTTPException 500: Se falhar ao processar
    """
    try:
        orchestrator = get_conversation_orchestrator()
        
        result = await orchestrator.process_inbound_message(
            chat_id=request.chat_id,
            phone_number=request.phone_number,
            message_text=request.message_text,
            session_name=request.session_name,
        )
        
        return ProcessMessageResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        ) from e


@router.get(
    "/stats",
    response_model=AIStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obter estatísticas de IA",
    description="""
    Retorna estatísticas de uso da IA:
    - Total de conversas
    - Total de interações LLM
    - Tokens usados
    - Latência média
    - Documentos no ChromaDB
    """,
)
async def get_ai_stats() -> AIStatsResponse:
    """
    Obter estatísticas de uso da IA.
    
    Returns:
        Estatísticas agregadas
        
    Raises:
        HTTPException 500: Se falhar ao obter stats
    """
    try:
        from robbot.adapters.repositories.conversation_repository import (
            ConversationRepository
        )
        from robbot.adapters.repositories.llm_interaction_repository import (
            LLMInteractionRepository
        )
        from robbot.infra.db.session import get_sync_session
        from robbot.infra.vectordb.chroma_client import get_chroma_client
        
        with get_sync_session() as session:
            conv_repo = ConversationRepository(session)
            llm_repo = LLMInteractionRepository(session)
            chroma = get_chroma_client()
            
            # Contar conversas
            all_conversations = conv_repo.get_all()
            total_conversations = len(all_conversations)
            
            # Contar interações LLM
            all_llm = llm_repo.get_all()
            total_llm_interactions = len(all_llm)
            
            # Calcular tokens e latência
            total_tokens = sum(llm.tokens_used for llm in all_llm)
            avg_latency = (
                sum(llm.latency_ms for llm in all_llm) / len(all_llm)
                if all_llm else 0
            )
            
            # ChromaDB
            chromadb_count = chroma.count()
            
            return AIStatsResponse(
                total_conversations=total_conversations,
                total_llm_interactions=total_llm_interactions,
                total_tokens_used=total_tokens,
                average_latency_ms=round(avg_latency, 2),
                chromadb_documents=chromadb_count,
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI stats: {str(e)}"
        ) from e
