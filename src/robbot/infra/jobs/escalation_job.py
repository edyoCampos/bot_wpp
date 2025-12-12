"""
Job para escalar conversa para secretária.
"""

import logging
from typing import Any, Optional

from robbot.adapters.repositories.conversation_repository import ConversationRepository
from robbot.domain.enums import ConversationStatus, LeadStatus
from robbot.infra.jobs.base_job import BaseJob, JobRetryableError, JobFailureError

logger = logging.getLogger(__name__)


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
        user_name: Optional[str] = None,
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
        super().__init__(**kwargs)
        
        self.conversation_id = conversation_id
        self.reason = reason
        self.phone = phone
        self.user_name = user_name or "Usuário"
        
        self.metadata.update({
            "conversation_id": conversation_id,
            "reason": reason,
            "phone": phone,
        })

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
            f"Escalando conversa {self.conversation_id} para secretária. "
            f"Motivo: {self.reason}",
            extra=self._log_context(),
        )
        
        try:
            # Atualizar status da conversa
            conv_repo = ConversationRepository()
            conversation = conv_repo.get_by_id(self.conversation_id)
            
            if not conversation:
                raise JobFailureError(f"Conversa {self.conversation_id} não encontrada")
            
            # Atualizar status
            updated_conv = conv_repo.update(
                self.conversation_id,
                {
                    "status": ConversationStatus.WAITING_SECRETARY,
                    "lead_status": LeadStatus.READY,
                    "escalated_at": None,  # Timestamp será preenchido pelo BD
                    "escalation_reason": self.reason,
                }
            )
            
            logger.info(
                f"✓ Conversa marcada como aguardando secretária",
                extra=self._log_context(),
            )
            
            # TODO: Criar notificação para secretária (push, email, webhook)
            notification_id = self._create_secretary_notification(conversation)
            
            # TODO: Atualizar lead status em sistema externo se necessário
            # (CRM, analytics, etc)
            
            return {
                "status": "success",
                "conversation_id": self.conversation_id,
                "notification_id": notification_id,
                "secretary_assignment": "next_available",  # TODO: implementar lógica de atribuição
                "context_prepared": True,
                "phone": self.phone,
                "user_name": self.user_name,
            }

        except Exception as e:
            logger.error(
                f"Erro ao escalar conversa: {type(e).__name__}: {e}",
                extra=self._log_context(),
            )
            
            # Se for erro de BD, pode retryar
            if "database" in str(e).lower() or "connection" in str(e).lower():
                raise JobRetryableError(f"Erro de BD: {e}")
            else:
                raise

    def _create_secretary_notification(self, conversation: Any) -> str:
        """
        Criar notificação para secretária.
        
        Args:
            conversation: Objeto de conversa
            
        Returns:
            ID da notificação criada
        """
        logger.debug(
            f"Criando notificação para secretária",
            extra=self._log_context(),
        )
        
        # TODO: Implementar:
        # - Criar registro em BD (notifications/tasks table)
        # - Enviar push notification via Firebase/OneSignal
        # - Enviar webhook para dashboard real-time
        
        notification_id = f"notif_{self.conversation_id}_{int(self.metadata.get('created_at', 0))}"
        return notification_id


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
            f"Escalando {len(self.conversation_ids)} conversas. Motivo: {self.reason}",
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
                
            except Exception as e:
                logger.warning(
                    f"Falha ao escalar {conv_id}: {e}",
                    extra=self._log_context(),
                )
                failed += 1
        
        logger.info(
            f"Escalação em lote concluída: {escalated} OK, {failed} falhadas",
            extra=self._log_context(),
        )
        
        return {
            "status": "completed",
            "escalated": escalated,
            "failed": failed,
            "total": len(self.conversation_ids),
        }
