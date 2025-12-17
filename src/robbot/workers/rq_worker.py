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
import sys
from typing import List

from rq import Worker
from rq.job import Job

from robbot.config.settings import settings
from robbot.infra.redis.client import get_redis_client
from robbot.infra.redis.queue import get_queue_manager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def exception_handler(job: Job, exc_type, exc_value, traceback):
    """
    Handler customizado para exceções em jobs.
    
    Registra erro detalhado e pode enviar alertas se necessário.
    """
    logger.error(
        f"Job {job.id} falhou: {exc_type.__name__}: {exc_value}",
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
    
    # TODO: Integrar com sistema de alertas (Sentry, email, etc)
    # if isinstance(exc_value, CriticalError):
    #     send_alert_to_admin(job, exc_value)


def main():
    """Inicializar e rodar worker RQ."""
    logger.info("=" * 80)
    logger.info("🚀 Iniciando RQ Worker")
    logger.info("=" * 80)
    logger.info(f"Redis URL: {settings.REDIS_URL}")
    logger.info(f"Max retries: {settings.RQ_MAX_RETRIES}")
    
    # Obter conexão Redis
    redis_conn = get_redis_client()
    
    # Testar conexão
    try:
        redis_conn.ping()
        logger.info("✓ Conexão com Redis estabelecida")
    except (ConnectionError, TimeoutError) as e:
        logger.error(f"✗ Falha ao conectar com Redis: {e}")
        sys.exit(1)
    
    # Obter filas
    queue_manager = get_queue_manager(redis_conn)
    queues = [
        queue_manager.queue_messages,    # Prioridade alta
        queue_manager.queue_ai,          # Prioridade média
        queue_manager.queue_escalation,  # Prioridade baixa
    ]
    
    logger.info(f"✓ Filas configuradas: {[q.name for q in queues]}")
    logger.info("=" * 80)
    
    # Criar worker com nome único baseado no hostname
    import socket
    worker_name = f"worker-{socket.gethostname()}"
    
    worker = Worker(
        queues,
        connection=redis_conn,
        name=worker_name,
        exception_handlers=[exception_handler],
    )
    
    # Log de startup
    logger.info(f"Worker ID: {worker.name}")
    logger.info("Aguardando jobs...")
    logger.info("Pressione Ctrl+C para parar")
    logger.info("=" * 80)
    
    # Iniciar processamento (blocking)
    try:
        worker.work(
            with_scheduler=True,  # Suporta jobs agendados
            logging_level="INFO",
        )
    except KeyboardInterrupt:
        logger.info("\n🛑 Worker interrompido pelo usuário")
        sys.exit(0)
    except (ValueError, RuntimeError, ConnectionError) as e:
        logger.error(f"✗ Worker crashed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
