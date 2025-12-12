"""
Factory para Redis Queue (RQ) com filas separadas por prioridade.
"""

import logging
from typing import Optional

from redis import Redis
from rq import Queue, Worker
from rq.job import Job

from robbot.config.settings import settings
from robbot.infra.redis.client import get_redis_client

logger = logging.getLogger(__name__)


class RQQueueManager:
    """
    Gerenciador centralizado de filas RQ.
    
    Responsabilidades:
    - Gerenciar filas separadas (messages, ai, escalation)
    - Fornecer acesso à fila de jobs falhados (DLQ)
    - Configurar retry policy e timeouts
    """

    def __init__(self, redis_client: Optional[Redis] = None):
        """
        Inicializa o gerenciador de filas.
        
        Args:
            redis_client: Cliente Redis (usa singleton se não fornecido)
        """
        self.redis_client = redis_client or get_redis_client()
        
        # Inicializar filas com configs específicas
        self._queue_messages: Optional[Queue] = None
        self._queue_ai: Optional[Queue] = None
        self._queue_escalation: Optional[Queue] = None
        self._queue_failed: Optional[Queue] = None

    @property
    def queue_messages(self) -> Queue:
        """Fila para processamento de mensagens (timeout: 10s)."""
        if self._queue_messages is None:
            self._queue_messages = Queue(
                name="messages",
                connection=self.redis_client,
                default_timeout=settings.RQ_JOB_TIMEOUT_MESSAGE,
                is_async=True,
            )
            logger.info(
                f"✓ Fila 'messages' inicializada (timeout={settings.RQ_JOB_TIMEOUT_MESSAGE}s)"
            )
        return self._queue_messages

    @property
    def queue_ai(self) -> Queue:
        """Fila para processamento de IA/Gemini (timeout: 60s)."""
        if self._queue_ai is None:
            self._queue_ai = Queue(
                name="ai",
                connection=self.redis_client,
                default_timeout=settings.RQ_JOB_TIMEOUT_AI,
                is_async=True,
            )
            logger.info(
                f"✓ Fila 'ai' inicializada (timeout={settings.RQ_JOB_TIMEOUT_AI}s)"
            )
        return self._queue_ai

    @property
    def queue_escalation(self) -> Queue:
        """Fila para escalação (transferência para secretária) (timeout: 30s)."""
        if self._queue_escalation is None:
            self._queue_escalation = Queue(
                name="escalation",
                connection=self.redis_client,
                default_timeout=settings.RQ_JOB_TIMEOUT_ESCALATION,
                is_async=True,
            )
            logger.info(
                f"✓ Fila 'escalation' inicializada (timeout={settings.RQ_JOB_TIMEOUT_ESCALATION}s)"
            )
        return self._queue_escalation

    @property
    def queue_failed(self) -> Queue:
        """Fila de jobs falhados (Dead Letter Queue)."""
        if self._queue_failed is None:
            self._queue_failed = Queue(
                name=settings.RQ_FAILED_QUEUE_NAME,
                connection=self.redis_client,
                is_async=True,
            )
            logger.info(f"✓ Fila 'failed' (DLQ) inicializada")
        return self._queue_failed

    def get_queue(self, queue_name: str) -> Queue:
        """
        Obter fila por nome.
        
        Args:
            queue_name: Nome da fila ('messages', 'ai', 'escalation')
            
        Returns:
            Instância de Queue
            
        Raises:
            ValueError: Se fila não existir
        """
        queues = {
            "messages": self.queue_messages,
            "ai": self.queue_ai,
            "escalation": self.queue_escalation,
            "failed": self.queue_failed,
        }
        
        if queue_name not in queues:
            raise ValueError(
                f"Fila '{queue_name}' não existe. Opções: {list(queues.keys())}"
            )
        
        return queues[queue_name]

    def get_all_queues(self) -> dict[str, Queue]:
        """Retorna dicionário com todas as filas."""
        return {
            "messages": self.queue_messages,
            "ai": self.queue_ai,
            "escalation": self.queue_escalation,
            "failed": self.queue_failed,
        }

    def get_queue_stats(self) -> dict[str, dict]:
        """
        Retorna estatísticas de todas as filas.
        
        Returns:
            Dict com count, size (bytes) e workers por fila
        """
        stats = {}
        for name, queue in self.get_all_queues().items():
            try:
                count = queue.count
                workers = Worker.all(connection=self.redis_client)
                workers_on_queue = [w for w in workers if queue.name in [q.name for q in w.queues]]
                
                stats[name] = {
                    "job_count": count,
                    "worker_count": len(workers_on_queue),
                    "failed_count": len(queue.failed_job_ids),
                }
            except Exception as e:
                logger.error(f"Erro ao obter stats da fila '{name}': {e}")
                stats[name] = {"error": str(e)}
        
        return stats

    def health_check(self) -> dict[str, bool]:
        """
        Verifica saúde de todas as filas e conexão Redis.
        
        Returns:
            Dict com status de cada fila
        """
        try:
            # Testar conexão com Redis
            self.redis_client.ping()
            
            # Verificar cada fila
            return {
                "redis": True,
                "queue_messages": bool(self.queue_messages),
                "queue_ai": bool(self.queue_ai),
                "queue_escalation": bool(self.queue_escalation),
                "queue_failed": bool(self.queue_failed),
            }
        except Exception as e:
            logger.error(f"Health check falhou: {e}")
            return {
                "redis": False,
                "error": str(e),
            }


# Singleton global
_queue_manager: Optional[RQQueueManager] = None


def get_queue_manager(redis_client: Optional[Redis] = None) -> RQQueueManager:
    """
    Obter instância singleton do gerenciador de filas.
    
    Args:
        redis_client: Redis client (uso interno)
        
    Returns:
        RQQueueManager singleton
    """
    global _queue_manager
    
    if _queue_manager is None:
        _queue_manager = RQQueueManager(redis_client)
        logger.info("🎯 RQQueueManager inicializado como singleton")
    
    return _queue_manager


def close_queue_manager() -> None:
    """Fechar gerenciador (limpar resources)."""
    global _queue_manager
    if _queue_manager is not None:
        logger.info("Fechando RQQueueManager")
        _queue_manager = None
