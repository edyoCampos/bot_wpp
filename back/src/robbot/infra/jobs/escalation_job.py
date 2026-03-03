"""
Job para escalar conversa para secretária.
"""

import logging
from typing import Any

from robbot.infra.persistence.repositories.conversation_repository import ConversationRepository
from robbot.domain.shared.enums import ConversationStatus, LeadStatus
from robbot.infra.db.session import get_sync_session
from robbot.infra.jobs.base_job import BaseJob, JobFailureError, JobRetryableError

logger = logging.getLogger(__name__)


def process_escalation_job(conversation_id: str, reason: str, phone: str, user_name: str | None) -> dict[str, Any]:
    """
    Module-level function for RQ to import and execute escalation jobs.

    This function creates an EscalationJob instance and runs it.
    """
    job = EscalationJob(conversation_id, reason, phone, user_name)
    return job.run()


class EscalationJob(BaseJob):
    """
    Job para transferir conversa para atendimento humano.

    Responsabilidades:
    - Validar maturidade do lead
    - Marcar conversa como aguardando secretária
    - Criar notificação para secretária
    - Persistir reason da escalação
    - Preparar contexto para transferência
    """

    def __init__(
        self,
        conversation_id: str,
        reason: str,
        phone: str,
        user_name: str | None = None,
        **kwargs,
    ):
        """
        Inicializar job de escalação.

        Args:
            conversation_id: ID da conversa
            reason: Motivo da escalação ("scheduling_request", "issue", "sentiment")
            phone: Telefone do usuário
            user_name: Nome do usuário (se disponível)
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
        self.reason = reason
        self.phone = phone
        self.user_name = user_name or "Usuário"

        self.metadata.update(
            {
                "conversation_id": conversation_id,
                "reason": reason,
                "phone": phone,
            }
        )

    def execute(self) -> dict[str, Any]:
        """
        Executar escalação.

        Returns:
            Dict com status, ID da notificação, contexto para secretária

        Raises:
            JobRetryableError: Se BD indisponível
            JobFailureError: Se conversa não pode ser escalada
        """
        logger.info(
            "Escalando conversa %s para secretária. Motivo: %s",
            self.conversation_id,
            self.reason,
            extra=self._log_context(),
        )

        try:
            with get_sync_session() as db:
                # Atualizar status da conversa
                conv_repo = ConversationRepository(db)
                conversation = conv_repo.get_by_id(self.conversation_id)

                if not conversation:
                    raise JobFailureError(f"Conversa {self.conversation_id} não encontrada")

                # Atualizar status
                conversation.status = ConversationStatus.WAITING_SECRETARY
                conversation.lead_status = LeadStatus.READY
                conversation.escalated_at = None  # Timestamp será preenchido pelo BD
                conversation.escalation_reason = self.reason
                conv_repo.update(conversation)

                logger.info(
                    "[SUCCESS] Conversation marked as waiting for secretary",
                    extra=self._log_context(),
                )

                # Criar notificação para secretária
                notification_id = self._create_secretary_notification()

                # Atualizar lead status em sistema externo se necessário (CRM, analytics, etc)

                return {
                    "status": "success",
                    "conversation_id": self.conversation_id,
                    "notification_id": notification_id,
                    "secretary_assignment": "next_available",
                    "context_prepared": True,
                    "phone": self.phone,
                    "user_name": self.user_name,
                }

        except (ValueError, JobFailureError) as e:
            logger.error(
                "Erro ao escalar conversa: %s: %s",
                type(e).__name__,
                e,
                extra=self._log_context(),
            )
            raise
        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error(
                "Erro inesperado ao escalar conversa: %s: %s",
                type(e).__name__,
                e,
                extra=self._log_context(),
            )
            # Se for erro de BD, pode retryar
            if "database" in str(e).lower() or "connection" in str(e).lower():
                raise JobRetryableError(f"Erro de BD: {e}") from e
            raise JobRetryableError(f"Erro inesperado: {e}") from e

    def _create_secretary_notification(self) -> str:
        """
        Criar notificação para secretária.

        Returns:
            ID da notificação criada
        """
        logger.debug(
            "Criando notificação para secretária",
            extra=self._log_context(),
        )

        # Implementação futura:
        # - Criar registro em BD (notifications/tasks table)
        # - Enviar push notification via Firebase/OneSignal
        # - Enviar webhook para dashboard real-time

        return f"notif_{self.conversation_id}_{int(self.metadata.get('created_at', 0))}"


class MultipleEscalationJob(BaseJob):
    """
    Job para escalar múltiplas conversas.

    Útil para: roubo de leads, transferência em lote, etc.
    """

    def __init__(
        self,
        conversation_ids: list[str],
        reason: str,
        **kwargs,
    ):
        """Inicializar job de escalação em lote."""
        super().__init__(**kwargs)

        self.conversation_ids = conversation_ids
        self.reason = reason

    def execute(self) -> dict[str, Any]:
        """Escalar múltiplas conversas."""
        escalated = 0
        failed = 0

        logger.info(
            "Escalando %s conversas. Motivo: %s",
            len(self.conversation_ids),
            self.reason,
            extra=self._log_context(),
        )

        for conv_id in self.conversation_ids:
            try:
                job = EscalationJob(
                    conversation_id=conv_id,
                    reason=self.reason,
                    phone="",
                    attempt=0,
                )
                job.run()
                escalated += 1

            except (JobFailureError, JobRetryableError, ValueError) as e:
                logger.warning(
                    "Falha ao escalar %s: %s",
                    conv_id,
                    e,
                    extra=self._log_context(),
                )
                failed += 1

        logger.info(
            "Escalação em lote concluída: %s OK, %s falhadas",
            escalated,
            failed,
            extra=self._log_context(),
        )

        return {
            "status": "completed",
            "escalated": escalated,
            "failed": failed,
            "total": len(self.conversation_ids),
        }

