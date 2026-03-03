"""Worker dedicado para executar polling periódico de mensagens WAHA."""

import logging
import time
from datetime import UTC, datetime

from rq.job import Job, JobStatus

from robbot.config.settings import get_settings
from robbot.core.logging_setup import configure_logging
from robbot.infra.redis.client import get_redis_client
from robbot.services.infrastructure.queue_service import get_queue_service

# Configuração global de logging para o processo
configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


def run_polling_worker():
    """
    Executa polling de mensagens WAHA a cada intervalo configurado.
    """
    queue_service = get_queue_service()
    redis_client = get_redis_client()
    polling_interval = getattr(settings, "WAHA_POLLING_INTERVAL", 10)

    logger.info(
        "=== WAHA POLLING WORKER INICIADO ===",
        extra={
            "interval_seconds": polling_interval,
            "dev_mode": settings.DEV_MODE,
        },
    )

    while True:
        try:
            now = datetime.now(UTC)
            job_func_path = "robbot.infra.jobs.message_polling_job.poll_waha_messages"
            
            job_id_val = queue_service.enqueue_custom(
                func=job_func_path,
                queue_name="messages",
                job_id=f"waha-polling-{int(now.timestamp())}",
                timeout=120,
            )

            if job_id_val:
                logger.info("[POLLING WORKER] Job enfileirado: %s", job_id_val)
                
                # Aguardar conclusão para evitar sobreposição se o job demorar
                try:
                    job = Job.fetch(job_id_val, connection=redis_client)
                    start_wait = time.time()
                    while job.get_status() not in [JobStatus.FINISHED, JobStatus.FAILED]:
                        if time.time() - start_wait > 125: # Pouco mais que o timeout do job
                            break
                        time.sleep(1)
                except Exception as e:
                    logger.error("[POLLING WORKER] Erro ao monitorar job: %s", e)
            
        except Exception as e:
            logger.error("[POLLING WORKER] Erro inesperado: %s", e, exc_info=True)

        time.sleep(polling_interval)


if __name__ == "__main__":
    run_polling_worker()
