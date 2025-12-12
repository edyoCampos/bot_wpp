"""
Job para agendamentos/tarefas futuras.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Optional

from robbot.infra.jobs.base_job import BaseJob, JobRetryableError

logger = logging.getLogger(__name__)


class ScheduledJob(BaseJob):
    """
    Job base para execução agendada.
    
    Responsabilidades:
    - Executar tarefa em data/hora específica
    - Logging de execução
    - Retry se falhar
    """

    def __init__(
        self,
        scheduled_for: datetime,
        task_type: str,
        task_data: dict[str, Any],
        **kwargs,
    ):
        """
        Inicializar job agendado.
        
        Args:
            scheduled_for: Data/hora para executar
            task_type: Tipo de tarefa ("reminder", "cleanup", "sync", "webhook")
            task_data: Dados da tarefa
            **kwargs: Argumentos herdados
        """
        super().__init__(**kwargs)
        
        self.scheduled_for = scheduled_for
        self.task_type = task_type
        self.task_data = task_data
        
        # Validação
        if scheduled_for < datetime.utcnow():
            raise ValueError(f"Agendamento no passado: {scheduled_for}")
        
        self.metadata.update({
            "scheduled_for": scheduled_for.isoformat(),
            "task_type": task_type,
        })

    def execute(self) -> dict[str, Any]:
        """
        Executar tarefa agendada.
        
        Returns:
            Dict com resultado da execução
        """
        logger.info(
            f"Executando tarefa agendada: {self.task_type}",
            extra=self._log_context(),
        )
        
        # Validar que não expirou
        now = datetime.utcnow()
        if now < self.scheduled_for:
            delay = (self.scheduled_for - now).total_seconds()
            logger.warning(
                f"Tarefa agendada para daqui {delay:.0f}s. Aguardando...",
                extra=self._log_context(),
            )
            return {"status": "scheduled", "seconds_until": delay}
        
        try:
            # Executar tarefa conforme tipo
            result = self._execute_task()
            
            logger.info(
                f"✓ Tarefa agendada concluída",
                extra=self._log_context(),
            )
            
            return result

        except Exception as e:
            logger.error(
                f"Erro em tarefa agendada: {type(e).__name__}: {e}",
                extra=self._log_context(),
            )
            raise JobRetryableError(str(e))

    def _execute_task(self) -> dict[str, Any]:
        """Executar tarefa específica (override em subclasses)."""
        # TODO: Implementar por tipo
        return {"status": "executed", "task_type": self.task_type}


class ReminderJob(ScheduledJob):
    """
    Job para lembrete de consulta.
    
    Envia mensagem WhatsApp lembrando about agendamento.
    """

    def __init__(
        self,
        conversation_id: str,
        appointment_id: str,
        phone: str,
        appointment_time: datetime,
        **kwargs,
    ):
        """Inicializar job de lembrete."""
        super().__init__(
            scheduled_for=appointment_time - timedelta(hours=24),
            task_type="reminder",
            task_data={
                "conversation_id": conversation_id,
                "appointment_id": appointment_id,
                "phone": phone,
                "appointment_time": appointment_time.isoformat(),
            },
            **kwargs,
        )
        
        self.conversation_id = conversation_id
        self.appointment_id = appointment_id
        self.phone = phone
        self.appointment_time = appointment_time

    def _execute_task(self) -> dict[str, Any]:
        """Enviar lembrete."""
        logger.info(
            f"Enviando lembrete de consulta para {self.phone}",
            extra=self._log_context(),
        )
        
        # TODO: Implementar:
        # - Recuperar dados da consulta
        # - Formatar mensagem
        # - Enfileirar para envio via WAHA
        
        return {
            "status": "reminder_sent",
            "conversation_id": self.conversation_id,
            "appointment_id": self.appointment_id,
            "phone": self.phone,
        }


class CleanupJob(ScheduledJob):
    """
    Job para limpeza periódica de dados.
    
    Tasks:
    - Remover conversas antigas (> 90 dias)
    - Limpar cache do ChromaDB
    - Arquivar dados de jobs completados
    """

    def __init__(
        self,
        cleanup_type: str = "all",
        days_threshold: int = 90,
        **kwargs,
    ):
        """
        Inicializar job de cleanup.
        
        Args:
            cleanup_type: "all", "conversations", "chroma", "jobs"
            days_threshold: Número de dias para considerar "antigo"
        """
        super().__init__(
            scheduled_for=datetime.utcnow() + timedelta(hours=1),
            task_type="cleanup",
            task_data={
                "cleanup_type": cleanup_type,
                "days_threshold": days_threshold,
            },
            **kwargs,
        )
        
        self.cleanup_type = cleanup_type
        self.days_threshold = days_threshold

    def _execute_task(self) -> dict[str, Any]:
        """Executar cleanup."""
        logger.info(
            f"Executando cleanup: {self.cleanup_type}",
            extra=self._log_context(),
        )
        
        cutoff_date = datetime.utcnow() - timedelta(days=self.days_threshold)
        
        results = {
            "status": "completed",
            "cleanup_type": self.cleanup_type,
            "cutoff_date": cutoff_date.isoformat(),
            "items_removed": 0,
        }
        
        # TODO: Implementar cleanup por tipo
        
        return results


class SyncJob(ScheduledJob):
    """
    Job para sincronização com sistemas externos.
    
    Tasks:
    - Sync de agendamentos com calendário
    - Sync de leads com CRM
    - Sync de métricas com analytics
    """

    def __init__(
        self,
        sync_target: str,  # "calendar", "crm", "analytics"
        **kwargs,
    ):
        """Inicializar job de sync."""
        super().__init__(
            scheduled_for=datetime.utcnow() + timedelta(minutes=30),
            task_type="sync",
            task_data={"sync_target": sync_target},
            **kwargs,
        )
        
        self.sync_target = sync_target

    def _execute_task(self) -> dict[str, Any]:
        """Executar sync."""
        logger.info(
            f"Sincronizando com {self.sync_target}",
            extra=self._log_context(),
        )
        
        # TODO: Implementar sync conforme target
        
        return {
            "status": "synced",
            "sync_target": self.sync_target,
            "items_synced": 0,
        }
