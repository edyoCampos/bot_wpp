"""
Autoscaling automático de workers baseado na carga das filas.

Este script deve ser executado periodicamente (ex: a cada 2 minutos)
para ajustar automaticamente o número de workers.

Regras:
- Mínimo: 2 workers (sempre)
- Máximo: 5 workers
- Scale UP: quando jobs/worker > 5
- Scale DOWN: quando todos workers ociosos e fila vazia

Uso:
    python scripts/autoscale_workers.py

    # Via cron (a cada 2 minutos):
    */2 * * * * cd /path/to/project && python scripts/autoscale_workers.py >> /var/log/autoscale.log 2>&1
"""

import logging
import subprocess
import sys

from robbot.core.logging_setup import configure_logging
from robbot.services.infrastructure.worker_analytics_service import WorkerAnalyticsService

logger = logging.getLogger("autoscaler")


def execute_scaling(target_workers: int) -> bool:
    """Execute docker-compose scale command via docker.sock."""
    try:
        compose_bin = "/usr/local/bin/docker-compose"
        # Use 'up -d --no-recreate --scale worker=N' to ONLY scale worker service
        # --no-recreate prevents restarting other services (including autoscaler itself)
        cmd = [compose_bin, "up", "-d", "--no-recreate", "--scale", f"wk={target_workers}", "wk"]
        cwd = "/app"

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd="/app"
        )

        if result.returncode == 0:
            logger.info("Scaled to %s workers", target_workers)
            return True
        else:
            logger.error("Scaling failed: rc=%s, stdout=%s, stderr=%s", result.returncode, result.stdout, result.stderr)
            return False

    except subprocess.TimeoutExpired:
        logger.error("Scaling command timed out")
        return False
    except Exception as e:
        logger.error("Scaling exception: %s", e)
        return False


def main():
    """Run autoscaling check and execute if needed."""
    # Ensure structured logging is configured for this script execution
    configure_logging(log_file="/tmp/autoscale.log")
    logger.info("Starting autoscaling check")

    try:
        service = WorkerAnalyticsService()
        should_scale, target, reason = service.should_autoscale()

        analytics = service.get_analytics()
        current_workers = analytics["workers"]["total"]
        pending_jobs = analytics["summary"]["total_pending"]

        logger.info("Current workers: %s, Pending jobs: %s", current_workers, pending_jobs)
        logger.info("Recommendation: %s - %s", analytics["autoscaling"]["action"], reason)

        if should_scale:
            logger.info("Executing scaling: %s -> %s workers", current_workers, target)
            success = execute_scaling(target)

            if success:
                logger.info("Autoscaling completed")
                return 0
            else:
                logger.error("Autoscaling failed")
                return 1
        else:
            logger.info("No scaling needed - system stable")
            return 0

    except Exception as e:
        logger.error("Fatal error during autoscaling: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
