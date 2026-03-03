"""
Worker RQ para processar jobs das filas.

Este worker processa jobs de múltiplas filas em ordem de prioridade:
1. messages (alta prioridade - processamento rápido)
2. ai (média prioridade - pode demorar mais)
3. escalation (baixa prioridade - transferências para secretária)

Uso:
    # Rodar localmente:
    python -m robbot.workers.rq_worker

    # Rodar via Docker:
    docker compose up -d worker

    # Monitorar workers:
    rq info --url redis://localhost:6379/0
"""

import logging
import socket
import sys

from rq import Worker
from rq.job import Job
from rq.registry import clean_registries

from robbot.config.settings import settings
from robbot.core.logging_setup import configure_logging
from robbot.infra.redis.client import get_redis_client
from robbot.infra.redis.queue import get_queue_manager

# Configurar logging estruturado
configure_logging()

logger = logging.getLogger(__name__)


def exception_handler(job: Job, exc_type, exc_value, traceback_):
    """
    Handler customizado para exceções em jobs.

    Registra erro detalhado e pode enviar alertas se necessário.
    """
    logger.error(
        "Job %s falhou: %s: %s",
        job.id,
        exc_type.__name__,
        exc_value,
        extra={
            "job_id": job.id,
            "queue": job.origin,
            "func_name": job.func_name,
            "args": job.args,
            "kwargs": job.kwargs,
            "exc_type": exc_type.__name__,
            "exc_value": str(exc_value),
        },
        exc_info=True,
    )

    # NOTE: Integrar com sistema de alertas (Sentry, email, etc)
    _ = traceback_  # consumed to avoid unused-argument warning


def main():
    """Inicializar e rodar worker RQ."""
    logger.info("Starting RQ Worker...")
    logger.info("Redis URL: %s", settings.REDIS_URL)
    logger.info("Max retries: %s", settings.RQ_MAX_RETRIES)

    # Sobrescrever a classe de death penalty globalmente
    import rq.defaults
    import rq.timeouts

    class NoDeathPenalty(rq.timeouts.BaseDeathPenalty):  # pyright: ignore[reportIncompatibleMethodOverride]
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def setup_death_penalty(self):
            """Não configurar nenhum sinal de morte."""
            logger.debug("NoDeathPenalty: setup_death_penalty called - doing nothing")

        def cancel_death_penalty(self):
            """Método abstrato implementado - não fazer nada."""
            logger.debug("NoDeathPenalty: cancel_death_penalty called - doing nothing")
            return

    rq.defaults.DEFAULT_DEATH_PENALTY_CLASS = NoDeathPenalty
    logger.info("Overrode DEFAULT_DEATH_PENALTY_CLASS with NoDeathPenalty")

    # Obter conexão Redis
    redis_conn = get_redis_client()

    # Test connection
    try:
        redis_conn.ping()
        logger.info("Connection to Redis established")
    except (ConnectionError, TimeoutError) as e:
        logger.error("Failed to connect to Redis: %s", e)
        sys.exit(1)

    # Get queues
    queue_manager = get_queue_manager(redis_conn)
    queues = [
        queue_manager.queue_messages,  # High priority
        queue_manager.queue_ai,  # Medium priority
        queue_manager.queue_escalation,  # Low priority
    ]

    logger.info("Queues configured: %s", [q.name for q in queues])

    # Clean stale worker registries before starting (prevents conflicts)
    # NOTE: clean_registries must be called per queue, not with a list
    for queue in queues:
        clean_registries(queue)
    logger.info("Cleaned stale worker registries")

    # Create worker with unique name based on hostname + PID + timestamp
    # Timestamp garante unicidade mesmo em restarts rápidos
    import os
    import time

    worker_name = f"worker-{socket.gethostname()}-{os.getpid()}-{int(time.time())}"

    # Force cleanup of any existing worker with similar name pattern
    # This prevents "worker already exists" errors on container restart
    try:
        all_workers = Worker.all(connection=redis_conn)  # type: ignore[attr-defined]
        for w in all_workers:
            if w.name.startswith(f"worker-{socket.gethostname()}"):
                logger.info("Removing stale worker registration: %s", w.name)
                try:
                    w.unregister()
                except Exception as e:  # pylint: disable=broad-except
                    logger.warning("Failed to unregister worker %s: %s", w.name, e)
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Failed to cleanup stale workers: %s", e)

    worker = Worker(
        queues,
        connection=redis_conn,
        name=worker_name,
        exception_handlers=[exception_handler],
        worker_ttl=420,  # 7 minutos - expira automaticamente se inativo
        job_monitoring_interval=3600,  # Verificar jobs a cada 1 hora (menos frequente)
    )

    # Log de startup
    logger.info("Worker ID: %s", worker.name)
    logger.info("Worker TTL: 420s (auto-expire if inactive)")
    logger.info("Waiting for jobs...")
    logger.info("Press Ctrl+C to stop")

    # Iniciar processamento (blocking)
    try:
        worker.work(
            with_scheduler=True,  # Suporta jobs agendados
            logging_level="INFO",
        )
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
        sys.exit(0)
    except (ValueError, RuntimeError, ConnectionError) as e:
        logger.error("Worker crashed: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
