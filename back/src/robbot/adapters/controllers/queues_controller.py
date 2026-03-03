"""
Queues controller for legacy test endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.services.infrastructure.queue_service import get_queue_service

router = APIRouter()


@router.get("/stats")
def get_queue_stats(_db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    queue_service = get_queue_service()
    _ = current_user

    try:
        stats = queue_service.get_queue_stats()
        queues_map = stats.get("queues", {})
        total_failed = sum(
            queue_stats.get("failed_count", 0) for queue_stats in queues_map.values() if isinstance(queue_stats, dict)
        )

        queue_list = []
        for name, queue_stats in queues_map.items():
            if isinstance(queue_stats, dict):
                queue_list.append(
                    {
                        "name": name,
                        "job_count": queue_stats.get("job_count", 0),
                        "worker_count": queue_stats.get("worker_count", 0),
                        "failed_count": queue_stats.get("failed_count", 0),
                    }
                )

        return {
            "queues": queue_list,
            "total_failed": total_failed,
        }
    except (ConnectionError, TimeoutError) as e:
        raise HTTPException(status_code=503, detail="Serviço de fila indisponível") from e
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Erro ao obter estatísticas") from e


@router.post("/retry/{job_id}")
def retry_failed_job(job_id: str, _db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    queue_service = get_queue_service()
    _ = current_user

    try:
        success = queue_service.retry_job(job_id)
        if not success:
            raise HTTPException(status_code=404, detail="Job não encontrado")
        return {"status": "success", "message": f"Job {job_id} reenfileirado para retry"}
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Erro ao retryar job") from e
