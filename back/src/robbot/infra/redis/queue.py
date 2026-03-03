"""
Factory para Redis Queue (RQ) com filas separadas por prioridade.
"""

import logging

from redis import Redis
from rq import Queue, Worker

from robbot.config.settings import settings
from robbot.core.custom_exceptions import QueueError
from robbot.infra.redis.client import get_redis_client

logger = logging.getLogger(__name__)


class RQQueueManager:
    """
    Gerenciador centralizado de filas RQ.
    """

    def __init__(self, redis_client: Redis | None = None):
        self.redis_client = redis_client or get_redis_client()
        self._queue_messages: Queue | None = None
        self._queue_ai: Queue | None = None
        self._queue_escalation: Queue | None = None
        self._queue_failed: Queue | None = None

    @property
    def queue_messages(self) -> Queue:
        if self._queue_messages is None:
            self._queue_messages = Queue(
                name="messages",
                connection=self.redis_client,
                default_timeout=settings.RQ_JOB_TIMEOUT_MESSAGE,
                is_async=True,
            )
        return self._queue_messages

    @property
    def queue_ai(self) -> Queue:
        if self._queue_ai is None:
            self._queue_ai = Queue(
                name="ai",
                connection=self.redis_client,
                default_timeout=settings.RQ_JOB_TIMEOUT_AI,
                is_async=True,
            )
        return self._queue_ai

    @property
    def queue_escalation(self) -> Queue:
        if self._queue_escalation is None:
            self._queue_escalation = Queue(
                name="escalation",
                connection=self.redis_client,
                default_timeout=settings.RQ_JOB_TIMEOUT_ESCALATION,
                is_async=True,
            )
        return self._queue_escalation

    @property
    def queue_failed(self) -> Queue:
        if self._queue_failed is None:
            self._queue_failed = Queue(
                name=settings.RQ_FAILED_QUEUE_NAME,
                connection=self.redis_client,
                is_async=True,
            )
        return self._queue_failed

    def get_queue(self, queue_name: str) -> Queue:
        queues = {
            "messages": self.queue_messages,
            "ai": self.queue_ai,
            "escalation": self.queue_escalation,
            "failed": self.queue_failed,
        }
        if queue_name not in queues:
            raise ValueError(f"Fila '{queue_name}' não existe.")
        return queues[queue_name]

_queue_manager: RQQueueManager | None = None

def get_queue_manager(redis_client: Redis | None = None) -> RQQueueManager:
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = RQQueueManager(redis_client)
        logger.info("[INFO] RQQueueManager initialized as singleton")
    return _queue_manager
