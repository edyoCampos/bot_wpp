"""
LangChain service for conversation memory and orchestration.

Este módulo fornece integração com LangChain para:
- Gerenciar memória de conversas
- Criar chains com contexto persistente
- Orquestrar fluxo de conversação
"""

import logging
from typing import Any, Optional

# LangChain 1.2.0+ usa langchain-core
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI

from robbot.config.settings import settings
from robbot.core.exceptions import ExternalServiceError
from robbot.core.custom_exceptions import LLMError

logger = logging.getLogger(__name__)


class LangChainService:
    """
    Service para LangChain conversation chains.
    
    Responsabilidades:
    - Criar e gerenciar ConversationChain
    - Manter memória de conversas
    - Integrar Gemini via LangChain
    """

    def __init__(self):
        """Inicializar LangChainService com Gemini."""
        try:
            # Configurar LLM (Gemini via LangChain)
            self.llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=settings.GEMINI_TEMPERATURE,
                max_tokens=settings.GEMINI_MAX_TOKENS,
            )
            
            logger.info(
                f"✓ LangChainService inicializado (model={settings.GEMINI_MODEL}, "
                f"temp={settings.GEMINI_TEMPERATURE})"
            )
            
        except Exception as e:
            logger.error(f"✗ Falha ao inicializar LangChainService: {e}", exc_info=True)
            raise ExternalServiceError(f"LangChain initialization failed: {e}") from e

    def create_conversation_chain(
        self,
        conversation_id: str,
        system_prompt: Optional[str] = None,
        memory_key: str = "history",
    ) -> InMemoryChatMessageHistory:
        """
        Criar chain de conversa com memória persistente.
        
        Args:
            conversation_id: ID único da conversa
            system_prompt: Prompt de sistema (opcional)
            memory_key: Chave para memória no contexto
            
        Returns:
            InMemoryChatMessageHistory configurada
            
        Raises:
            ExternalServiceError: Se falhar ao criar chain
        """
        try:
            # Criar memória de conversa (LangChain 1.2.0+)
            memory = InMemoryChatMessageHistory()
            
            # Adicionar system prompt se fornecido
            if system_prompt:
                from langchain_core.messages import SystemMessage
                memory.add_message(SystemMessage(content=system_prompt))
            
            logger.info(
                f"✓ ConversationChain criada (conv_id={conversation_id}, "
                f"has_system_prompt={bool(system_prompt)})"
            )
            
            return memory
            
        except Exception as e:
            logger.error(
                f"✗ Falha ao criar ConversationChain: {e}",
                exc_info=True,
                extra={"conversation_id": conversation_id}
            )
            raise ExternalServiceError(f"Failed to create conversation chain: {e}") from e

    def run_chain(
        self,
        chain: InMemoryChatMessageHistory,
        user_input: str,
        conversation_id: str,
    ) -> str:
        """
        Executar chain com input do usuário.
        
        Args:
            chain: InMemoryChatMessageHistory configurada
            user_input: Input do usuário
            conversation_id: ID da conversa (para logging)
            
        Returns:
            Resposta do LLM
            
        Raises:
            ExternalServiceError: Se falhar ao executar
        """
        try:
            from langchain_core.messages import HumanMessage, AIMessage
            
            logger.info(
                f"🤖 Executando chain (conv_id={conversation_id}, "
                f"input_length={len(user_input)})"
            )
            
            # Adicionar mensagem do usuário
            chain.add_message(HumanMessage(content=user_input))
            
            # Executar LLM com histórico
            response = self.llm.invoke(chain.messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Salvar resposta na memória
            chain.add_message(AIMessage(content=response_text))
            
            logger.info(
                f"✓ Chain executada com sucesso (conv_id={conversation_id}, "
                f"response_length={len(response_text)})"
            )
            
            return response_text
            
        except LLMError:
            raise
        except Exception as e:
            logger.error(
                f"✗ Falha ao executar chain: {e}",
                exc_info=True,
                extra={"conversation_id": conversation_id}
            )
            raise LLMError(service="LangChain", message=f"Failed to run conversation chain: {e}", original_error=e)

    def get_memory_messages(self, chain: InMemoryChatMessageHistory) -> list[dict[str, str]]:
        """
        Obter mensagens da memória da chain.
        
        Args:
            chain: InMemoryChatMessageHistory
            
        Returns:
            Lista de mensagens:
            [
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
        """
        try:
            messages = []
            
            # Processar mensagens do histórico (LangChain 1.2.0+)
            for msg in chain.messages:
                role = "assistant" if msg.type == "ai" else "user"
                messages.append({
                    "role": role,
                    "content": msg.content,
                })
            
            return messages
            
        except LLMError:
            raise
        except Exception as e:
            logger.error(f"✗ Falha ao obter mensagens da memória: {e}", exc_info=True)
            raise LLMError(service="LangChain", message=f"Failed to get memory messages: {e}", original_error=e)

    def clear_memory(self, chain: InMemoryChatMessageHistory) -> None:
        """
        Limpar memória da chain.
        
        Args:
            chain: InMemoryChatMessageHistory
        """
        try:
            chain.clear()
            logger.info("✓ Memória da chain limpa")
        except LLMError:
            raise
        except Exception as e:
            logger.error(f"✗ Falha ao limpar memória: {e}", exc_info=True)
            raise LLMError(service="LangChain", message=f"Failed to clear memory: {e}", original_error=e)


# Singleton global
_langchain_service: Optional[LangChainService] = None


def get_langchain_service() -> LangChainService:
    """
    Obter instância singleton do LangChainService.
    
    Returns:
        LangChainService singleton
    """
    global _langchain_service
    
    if _langchain_service is None:
        _langchain_service = LangChainService()
        logger.info("🎯 LangChainService inicializado como singleton")
    
    return _langchain_service


def close_langchain_service() -> None:
    """Fechar service (cleanup)."""
    global _langchain_service
    if _langchain_service is not None:
        logger.info("Fechando LangChainService")
        _langchain_service = None
