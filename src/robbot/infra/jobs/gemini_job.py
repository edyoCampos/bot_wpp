"""
Job para processar mensagens com Gemini AI.
"""

import logging
from typing import Any, Optional

from robbot.adapters.repositories.conversation_repository import ConversationRepository
from robbot.adapters.repositories.message_repository import MessageRepository
from robbot.core.custom_exceptions import DatabaseError
from robbot.infra.db.base import SessionLocal
from robbot.infra.jobs.base_job import BaseJob, JobRetryableError, JobFailureError

logger = logging.getLogger(__name__)


class GeminiAIProcessingJob(BaseJob):
    """
    Job para processar mensagem com IA Gemini.
    
    Responsabilidades:
    - Recuperar histórico de conversa
    - Chamar Gemini com LangChain
    - Validar resposta
    - Persistir resposta em BD
    - Enfileirar para envio
    """

    def __init__(
        self,
        conversation_id: str,
        message_id: str,
        user_input: str,
        phone: str,
        **kwargs,
    ):
        """
        Inicializar job de IA.
        
        Args:
            conversation_id: ID da conversa
            message_id: ID da mensagem de entrada
            user_input: Texto da mensagem do usuário
            phone: Número de telefone (para logging)
            **kwargs: Argumentos herdados
        """
        super().__init__(**kwargs)
        
        self.conversation_id = conversation_id
        self.message_id = message_id
        self.user_input = user_input
        self.phone = phone
        
        self.metadata.update({
            "conversation_id": conversation_id,
            "message_id": message_id,
            "phone": phone,
        })

    def execute(self) -> dict[str, Any]:
        """
        Executar processamento com IA.
        
        Returns:
            Dict com ID da resposta gerada e conteúdo
            
        Raises:
            JobRetryableError: Se IA ou BD indisponíveis
            JobFailureError: Se resposta inválida
        """
        logger.info(
            f"Processando com IA: {self.phone} -> '{self.user_input[:50]}...'",
            extra=self._log_context(),
        )
        
        db = SessionLocal()
        try:
            conversation_context = self._get_conversation_context()
            
            ai_response = self._call_gemini(conversation_context)
            
            self._validate_ai_response(ai_response)
            
            message_repo = MessageRepository(db)
            response_record = message_repo.create(
                conversation_id=self.conversation_id,
                direction="outbound",
                content=ai_response,
                message_type="text",
                phone=self.phone,
                metadata={
                    "generated_by": "gemini_ai",
                    "triggerd_by_message_id": self.message_id,
                },
            )
            
            logger.info(
                f"✓ Resposta IA persistida: {response_record.id}",
                extra=self._log_context(),
            )
            
            return {
                "status": "success",
                "response_id": response_record.id,
                "response_text": ai_response[:100],  # Preview
                "conversation_id": self.conversation_id,
                "phone": self.phone,
                "ready_for_sending": True,
            }

        except ValueError as e:
            logger.error(
                f"Resposta inválida de IA: {e}",
                extra=self._log_context(),
            )
            raise JobFailureError(str(e)) from e
        except Exception as e:
            logger.error(
                f"Erro ao processar com IA: {type(e).__name__}: {e}",
                extra=self._log_context(),
            )
            
            if any(x in str(e).lower() for x in ["timeout", "rate", "api", "503", "429"]):
                raise JobRetryableError(f"Erro de API IA: {e}") from e
            raise JobFailureError(str(e)) from e
        finally:
            db.close()

    def _get_conversation_context(self) -> str:
        """
        Recuperar histórico de conversa do ChromaDB/BD.
        
        Returns:
            String com contexto formatado para envio ao Gemini
        """
        db = SessionLocal()
        try:
            conv_repo = ConversationRepository(db)
            msg_repo = MessageRepository(db)
            
            conversation = conv_repo.get_by_id(self.conversation_id)
            if not conversation:
                raise ValueError(f"Conversa {self.conversation_id} não encontrada")
            
            messages = msg_repo.get_by_conversation_id(
                self.conversation_id,
                limit=10,
            )
            
            context_lines = []
            for msg in messages:
                direction = "Lead" if msg.direction == "inbound" else "Bot"
                context_lines.append(f"{direction}: {msg.content}")
            
            return "\n".join(context_lines)

        except DatabaseError:
            raise
        except Exception as e:
            logger.warning(
                f"Não foi possível recuperar contexto: {e}",
                extra=self._log_context(),
            )
            raise DatabaseError(f"Failed to retrieve context: {e}")
        finally:
            db.close()

    def _call_gemini(self, context: str) -> str:
        """
        Chamar API Gemini com LangChain.
        
        Args:
            context: Histórico formatado da conversa
            
        Returns:
            Resposta gerada pelo Gemini
            
        Raises:
            JobRetryableError: Se API indisponível
        """
        # Implementação futura: chamada real com LangChain
        # Por enquanto, resposta mock
        
        logger.debug(
            f"Chamando Gemini com contexto ({len(context)} chars)",
            extra=self._log_context(),
        )
        
        # Placeholder para desenvolvimento futuro
        return f"[Resposta do Gemini para: {self.user_input[:30]}...]"

    def _validate_ai_response(self, response: str) -> None:
        """
        Validar resposta de IA.
        
        Args:
            response: Texto da resposta
            
        Raises:
            ValueError: Se resposta inválida
        """
        if not response or len(response.strip()) == 0:
            raise ValueError("IA retornou resposta vazia")
        
        if len(response) > 4096:
            logger.warning(
                f"Resposta truncada: {len(response)} > 4096 chars",
                extra=self._log_context(),
            )
            response = response[:4096] + "..."


class MessageAnalysisJob(BaseJob):
    """
    Job para analisar mensagem e determinar próximas ações.
    
    Responsabilidades:
    - Classificar intent (pergunta, agendamento, feedback)
    - Detectar sentimento (positivo, negativo, neutro)
    - Decidir se precisa escalação
    - Atualizar status do lead
    """

    def __init__(
        self,
        conversation_id: str,
        message_id: str,
        message_text: str,
        **kwargs,
    ):
        """Inicializar job de análise."""
        super().__init__(**kwargs)
        
        self.conversation_id = conversation_id
        self.message_id = message_id
        self.message_text = message_text

    def execute(self) -> dict[str, Any]:
        """
        Analisar mensagem.
        
        Returns:
            Dict com classificação, intent, sentimento, recomendações
        """
        logger.info(
            f"Analisando mensagem: '{self.message_text[:50]}...'",
            extra=self._log_context(),
        )
        
        # Implementação futura: análise real com Gemini
        
        return {
            "status": "success",
            "intent": "question",  # "question", "booking", "feedback", "off-topic"
            "sentiment": "positive",  # "positive", "negative", "neutral"
            "needs_escalation": False,
            "confidence": 0.85,
            "recommendations": [
                "Continue com resposta automática",
            ],
        }
