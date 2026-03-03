"""
Service para orquestração de filas (jobs assíncronos).
"""

import json
import logging
from datetime import timedelta
from typing import Any
from uuid import uuid4

from robbot.config.settings import settings
from robbot.infra.redis.client import get_redis_client
from robbot.infra.redis.queue import get_queue_manager

logger = logging.getLogger(__name__)


class QueueService:
    """
    Service para gerenciar jobs assíncronos.
    """

    def __init__(self):
        """Inicializar serviço de filas."""
        self.queue_manager = get_queue_manager()
        logger.info("[SUCCESS] QueueService inicializado")

    def enqueue_custom(
        self,
        func: Any,
        queue_name: str = "messages",
        job_id: str | None = None,
        timeout: int = 300,
    ) -> str:
        """Enfileirar um job customizado (função ou string path)."""
        queue = self.queue_manager.get_queue(queue_name)
        
        # Determinar nome para logging sem quebrar se for string
        func_name = func if isinstance(func, str) else getattr(func, "__name__", str(func))

        enqueued_job = queue.enqueue(
            func,
            job_id=job_id,
            job_timeout=timeout,
        )
        
        # CRITICAL: Force timeout explicitly (RQ sometimes ignores job_timeout parameter)
        try:
            enqueued_job.timeout = timeout
            enqueued_job.save()
            logger.debug("Forced job timeout to %ds for job %s", timeout, enqueued_job.id)
        except Exception as e:
            logger.warning("Failed to force job timeout: %s", e)
        
        logger.info(
            "Job customizado enfileirado (fila: %s) -> %s",
            queue_name,
            enqueued_job.id,
            extra={
                "job_id": enqueued_job.id,
                "queue": queue_name,
                "function": func_name,
            },
        )
        return enqueued_job.id

    def enqueue_message_processing(
        self,
        message_data: dict[str, Any],
        conversation_id: str | None = None,
        message_direction: str = "inbound",
    ) -> str:
        """Enfileirar mensagem para processamento (usando string path para evitar circularidade)."""
        job_id = str(uuid4())

        enqueued_job = self.queue_manager.queue_messages.enqueue(
            "robbot.infra.jobs.message_job.process_message_job",
            message_data=message_data,
            message_direction=message_direction,
            conversation_id=conversation_id,
            user_id=None,
            job_id=job_id,
            timeout=600,
            result_ttl=settings.RQ_DEFAULT_RESULT_TTL,
            failure_ttl=settings.RQ_DEFAULT_FAILURE_TTL,
        )

        try:
            enqueued_job.timeout = 600
            enqueued_job.save()
        except Exception:
            pass

        return job_id

    def enqueue_message_processing_debounced(
        self,
        message_data: dict[str, Any],
        conversation_id: str | None = None,
        message_direction: str = "inbound",
    ) -> str:
        """Enfileirar mensagens com debounce."""
        if message_direction != "inbound":
            return self.enqueue_message_processing(message_data, conversation_id, message_direction)

        chat_id = message_data.get("from") or message_data.get("phone")
        if not chat_id:
            return self.enqueue_message_processing(message_data, conversation_id, message_direction)

        debounce_seconds = max(0, int(settings.MESSAGE_DEBOUNCE_SECONDS))
        if debounce_seconds == 0:
            return self.enqueue_message_processing(message_data, conversation_id, message_direction)

        redis_client = get_redis_client()
        buffer_key = f"waha:debounce:{chat_id}"
        job_key = f"waha:debounce:job:{chat_id}"

        existing = redis_client.get(buffer_key)
        payload = json.loads(existing) if existing else {"messages": [], "last_payload": {}}
        
        body = message_data.get("body", "")
        if isinstance(body, str) and body.strip():
            payload.setdefault("messages", []).append(body)

        payload["last_payload"] = {"session": message_data.get("session", "default")}
        redis_client.setex(buffer_key, debounce_seconds + 10, json.dumps(payload))

        if redis_client.set(job_key, "1", nx=True, ex=debounce_seconds + 30):
            delay = timedelta(seconds=debounce_seconds)
            self.queue_manager.queue_messages.enqueue_in(
                delay,
                "robbot.infra.jobs.message_job.process_debounced_message",
                chat_id=chat_id,
                result_ttl=settings.RQ_DEFAULT_RESULT_TTL,
                failure_ttl=settings.RQ_DEFAULT_FAILURE_TTL,
            )
            return f"debounced:{chat_id}"

        return f"buffered:{chat_id}"

    def enqueue_ai_processing(
        self,
        conversation_id: str,
        message_id: str,
        user_input: str,
        phone: str,
    ) -> str:
        """Enfileirar para IA usando string path."""
        job_id = str(uuid4())
        self.queue_manager.queue_ai.enqueue(
            "robbot.infra.jobs.gemini_job.process_gemini_job",
            conversation_id=conversation_id,
            message_id=message_id,
            user_input=user_input,
            phone=phone,
            job_id=job_id,
            result_ttl=settings.RQ_DEFAULT_RESULT_TTL,
            failure_ttl=settings.RQ_DEFAULT_FAILURE_TTL,
        )
        return job_id

    def enqueue_escalation(
        self,
        conversation_id: str,
        reason: str,
        phone: str,
        user_name: str | None = None,
    ) -> str:
        """Enfileirar escalação usando string path."""
        job_id = str(uuid4())
        self.queue_manager.queue_escalation.enqueue(
            "robbot.infra.jobs.escalation_job.process_escalation_job",
            conversation_id=conversation_id,
            reason=reason,
            phone=phone,
            user_name=user_name,
            job_id=job_id,
            result_ttl=settings.RQ_DEFAULT_RESULT_TTL,
            failure_ttl=settings.RQ_DEFAULT_FAILURE_TTL,
        )
        return job_id

    def health_check(self) -> dict[str, Any]:
        """Verifica saúde do serviço de filas (conexão Redis)."""
        try:
            # Verifica conexão Redis
            redis_client = get_redis_client()
            if not redis_client.ping():
                return {"status": "unhealthy", "error": "Redis ping failed"}
            
            # Opcional: Verificar tamanhos das filas (apenas para debug extra)
            # q_len = len(self.queue_manager.queue_messages)
            
            return {"status": "healthy"}
        except Exception as e:
            logger.error("Queue health check failed: %s", e)
            return {"status": "unhealthy", "error": str(e)}
# Singleton global
_queue_service: QueueService | None = None


def get_queue_service() -> QueueService:
    """Retorna singleton do serviço de filas."""
    global _queue_service
    if _queue_service is None:
        _queue_service = QueueService()
    return _queue_service
