"""
Controller para gerenciar filas/jobs.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.services.infrastructure.queue_service import get_queue_service

logger = logging.getLogger(__name__)

router = APIRouter()

# =====================================================================
# GET ENDPOINTS
# =====================================================================


@router.get("/stats")
def get_queue_stats(_db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Obter estatísticas de todas as filas.

    Requer: Autenticação
    Admin can see global stats, Users can see their own queued jobs.

    Returns:
        Dict com queue stats
    """
    queue_service = get_queue_service()

    try:
        stats = queue_service.get_queue_stats()

        logger.info(
            "Queue stats requisitados por %s",
            current_user.email,
            extra={"user_id": current_user.id, "role": current_user.role},
        )

        return {
            "status": "success",
            "data": stats,
        }

    except (ConnectionError, TimeoutError) as e:
        logger.error("[ERROR] Connection error getting queue stats: %s", e)
        raise HTTPException(status_code=503, detail="Serviço de fila indisponível") from e
    except Exception as e:  # noqa: BLE001 (blind exception)
        logger.error("Failed to get queue stats: %s", e)
        raise HTTPException(status_code=500, detail="Erro ao obter estatísticas") from e


@router.get("/health")
def queue_health_check():
    """
    Health check das filas (público).

    Returns:
        Status de cada fila
    """
    queue_service = get_queue_service()

    try:
        health = queue_service.health_check()

        status_code = 200 if health["status"] == "healthy" else 503
        return {
            "status": health["status"],
            "queues": health.get("queues", {}),
        }, status_code

    except (ConnectionError, TimeoutError) as e:
        logger.error("[ERROR] Connection error in queue health check: %s", e)
        return {"status": "unhealthy", "error": "Serviço de fila indisponível"}, 503
    except (KeyError, ValueError) as e:
        logger.error("[ERROR] Validation error in queue health check: %s", e)
        return {"status": "unhealthy", "error": str(e)}, 503


@router.get("/jobs/{job_id}")
def get_job_status(
    job_id: str,
    _db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Obter status de um job específico.

    Path Params:
        job_id: ID do job

    Returns:
        Status, resultado, erros
    """
    queue_service = get_queue_service()

    try:
        status = queue_service.get_job_status(job_id)

        logger.info(
            "Job status requisitado: %s",
            job_id,
            extra={"user_id": current_user.id, "job_id": job_id},
        )

        return {
            "status": "success",
            "data": status,
        }

    except Exception as e:  # noqa: BLE001 (blind exception)
        logger.error("Failed to get job status %s: %s", job_id, e)
        raise HTTPException(status_code=500, detail="Erro ao obter status") from e


@router.get("/failed")
def get_failed_jobs(
    limit: int = Query(10, ge=1, le=100),
    _db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Obter jobs falhados (DLQ).

    Requer: Role ADMIN

    Query Params:
        limit: Número máximo de jobs (default: 10)

    Returns:
        Lista de jobs na Dead Letter Queue
    """
    queue_service = get_queue_service()

    try:
        failed_jobs = queue_service.get_failed_jobs(limit=limit)

        logger.info(
            "Failed jobs requisitados por %s",
            current_user.email,
            extra={"user_id": current_user.id, "limit": limit},
        )

        return {
            "status": "success",
            "total": len(failed_jobs),
            "data": failed_jobs,
        }

    except Exception as e:  # noqa: BLE001 (blind exception)
        logger.error("Failed to get failed jobs: %s", e)
        raise HTTPException(status_code=500, detail="Erro ao obter failed jobs") from e


# =====================================================================
# POST ENDPOINTS (Ações)
# =====================================================================


@router.post("/jobs/{job_id}/retry")
def retry_job(
    job_id: str,
    _db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Retryar um job falhado.

    Requer: Role ADMIN

    Path Params:
        job_id: ID do job a retryar

    Returns:
        Status da operação
    """
    queue_service = get_queue_service()

    try:
        success = queue_service.retry_job(job_id)

        if not success:
            raise HTTPException(status_code=404, detail="Job não encontrado")

        logger.info(
            "Job %s retentado por %s",
            job_id,
            current_user.email,
            extra={"user_id": current_user.id, "job_id": job_id},
        )

        return {
            "status": "success",
            "message": f"Job {job_id} reenfileirado para retry",
        }

    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001 (blind exception)
        logger.error("[ERROR] Failed to retry job %s: %s", job_id, e)
        raise HTTPException(status_code=500, detail="Erro ao retryar job") from e


@router.post("/jobs/{job_id}/cancel")
def cancel_job(
    job_id: str,
    _db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Cancelar um job.

    Requer: Role ADMIN

    Path Params:
        job_id: ID do job a cancelar

    Returns:
        Status da operação
    """
    queue_service = get_queue_service()

    try:
        success = queue_service.cancel_job(job_id)

        if not success:
            raise HTTPException(status_code=404, detail="Job não encontrado ou já completado")

        logger.info(
            "Job %s cancelado por %s",
            job_id,
            current_user.email,
            extra={"user_id": current_user.id, "job_id": job_id},
        )

        return {
            "status": "success",
            "message": f"Job {job_id} cancelado",
        }

    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001 (blind exception)
        logger.error("[ERROR] Failed to cancel job %s: %s", job_id, e)
        raise HTTPException(status_code=500, detail="Erro ao cancelar job") from e


@router.post("/retry-failed")
def retry_failed_jobs(
    job_ids: list[str] | None = None,
    _db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Reprocessar jobs falhados em lote.

    Requer: Role ADMIN

    Body:
        job_ids: Lista opcional de IDs específicos. Se vazio, tenta todos os falhados.

    Returns:
        Contador de jobs retentados
    """
    queue_service = get_queue_service()

    try:
        if job_ids:
            # Retryar IDs específicos
            retried = 0
            for job_id in job_ids:
                if queue_service.retry_job(job_id):
                    retried += 1
        else:
            # Retryar todos os failed jobs
            retried = queue_service.retry_all_failed()

        logger.info(
            "%s failed jobs retentados por %s",
            retried,
            current_user.email,
            extra={"user_id": current_user.id, "retried": retried},
        )

        return {
            "status": "success",
            "retried": retried,
            "message": f"{retried} jobs reenfileirados para retry",
        }

    except Exception as e:  # noqa: BLE001 (blind exception)
        logger.error("[ERROR] Failed to retry failed jobs: %s", e)
        raise HTTPException(status_code=500, detail="Erro ao retryar jobs") from e


@router.delete("/clear-failed")
def clear_failed_jobs(
    _db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Limpar todos os jobs falhados (DLQ).

    [WARNING] ATENÇÃO: Esta operação é IRREVERSÍVEL!

    Requer: Role ADMIN

    Returns:
        Contador de jobs removidos
    """
    queue_service = get_queue_service()

    try:
        cleared = queue_service.clear_failed_queue()

        logger.warning(
            "Dead Letter Queue limpa por %s (%s jobs removidos)",
            current_user.email,
            cleared,
            extra={"user_id": current_user.id, "cleared": cleared},
        )

        return {
            "status": "success",
            "cleared": cleared,
            "message": f"{cleared} jobs removidos da DLQ",
        }

    except Exception as e:  # noqa: BLE001 (blind exception)
        logger.error("[ERROR] Failed to clear failed queue: %s", e)
        raise HTTPException(status_code=500, detail="Erro ao limpar failed queue") from e
