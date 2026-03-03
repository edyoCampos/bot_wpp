"""
Job para processar mensagens com Gemini AI.
"""

import logging
from typing import Any

from robbot.infra.persistence.repositories.conversation_message_repository import (
    ConversationMessageRepository,
)
from robbot.infra.persistence.repositories.conversation_repository import ConversationRepository
from robbot.infra.db.session import get_sync_session
from robbot.infra.jobs.base_job import BaseJob, JobFailureError, JobRetryableError

logger = logging.getLogger(__name__)


def process_gemini_job(conversation_id: str, message_id: str, user_input: str, phone: str) -> dict[str, Any]:
    """
    Module-level function for RQ to import and execute Gemini AI processing jobs.

    This function creates a GeminiAIProcessingJob instance and runs it.
    """
    job = GeminiAIProcessingJob(conversation_id, message_id, user_input, phone)
    return job.run()


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
        # Filter out RQ-specific kwargs that BaseJob doesn't accept
        base_job_kwargs = {}
        if "job_id" in kwargs:
            base_job_kwargs["job_id"] = kwargs["job_id"]
        if "attempt" in kwargs:
            base_job_kwargs["attempt"] = kwargs["attempt"]
        if "metadata" in kwargs:
            base_job_kwargs["metadata"] = kwargs["metadata"]

        super().__init__(**base_job_kwargs)

        self.conversation_id = conversation_id
        self.message_id = message_id
        self.user_input = user_input
        self.phone = phone

        self.metadata.update(
            {
                "conversation_id": conversation_id,
                "message_id": message_id,
                "phone": phone,
            }
        )

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
            "Processando com IA: %s -> '%s...'",
            self.phone,
            self.user_input[:50],
            extra=self._log_context(),
        )

        try:
            with get_sync_session() as db:
                conversation_context = self._get_conversation_context()

                ai_response = self._call_gemini(conversation_context)

                self._validate_ai_response(ai_response)

                conv_msg_repo = ConversationMessageRepository(db)
                from robbot.infra.persistence.models import MessageModel

                response_record = MessageModel(
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
                conv_msg_repo.create(response_record)  # type: ignore[attr-defined]

                logger.info(
                    "[SUCCESS] Resposta IA persistida: %s",
                    response_record.id,
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
                "Resposta inválida de IA: %s",
                e,
                extra=self._log_context(),
            )
            raise JobFailureError(str(e)) from e
        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error(
                "Erro ao processar com IA: %s: %s",
                type(e).__name__,
                e,
                extra=self._log_context(),
            )

            if any(x in str(e).lower() for x in ["timeout", "rate", "api", "503", "429"]):
                raise JobRetryableError(f"Erro de API IA: {e}") from e
            raise JobFailureError(str(e)) from e

    def _get_conversation_context(self) -> str:
        """
        Recuperar histórico de conversa do ChromaDB/BD.

        Returns:
            String com contexto formatado para envio ao Gemini
        """
        with get_sync_session() as db:
            conv_repo = ConversationRepository(db)
            conv_msg_repo = ConversationMessageRepository(db)

            conversation = conv_repo.get_by_id(self.conversation_id)
            if not conversation:
                raise ValueError(f"Conversa {self.conversation_id} não encontrada")

            messages = conv_msg_repo.get_by_conversation(
                conversation_id=self.conversation_id,
                limit=10,
            )

            context_lines = []
            for msg in messages:
                direction = "Lead" if msg.direction == "inbound" else "Bot"
                context_lines.append(f"{direction}: {msg.content}")

            return "\n".join(context_lines)

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
            "Chamando Gemini com contexto (%s chars)",
            len(context),
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
                "Resposta truncada: %s > 4096 chars",
                len(response),
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
            "Analisando mensagem: '%s...'",
            self.message_text[:50],
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

