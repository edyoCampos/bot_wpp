"""Worker analytics and management routes."""

import logging
import subprocess

from fastapi import APIRouter, Depends, HTTPException, status

from robbot.api.v1.dependencies import get_current_user
from robbot.schemas.worker import (
    AutoscalingConfig,
    ScaleWorkersRequest,
    WorkerAnalytics,
)
from robbot.services.infrastructure.worker_analytics_service import WorkerAnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workers", tags=["Workers"])


@router.get("/analytics", response_model=WorkerAnalytics)
def get_worker_analytics(
    _current_user=Depends(get_current_user),
):
    """Get worker analytics and queue statistics."""
    try:
        service = WorkerAnalyticsService()
        return service.get_analytics()
    except Exception as e:  # noqa: BLE001 (blind exception)
        logger.error("Failed to get worker analytics: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve worker analytics",
        ) from e


@router.get("/autoscaling/config", response_model=AutoscalingConfig)
def get_autoscaling_config(
    _current_user=Depends(get_current_user),
):
    """Get current autoscaling configuration."""
    service = WorkerAnalyticsService()
    return service.get_autoscaling_config()


@router.put("/autoscaling/config", response_model=AutoscalingConfig)
def update_autoscaling_config(
    config: AutoscalingConfig,
    _current_user=Depends(get_current_user),
):
    """Update autoscaling configuration."""
    service = WorkerAnalyticsService()
    return service.update_autoscaling_config(config.model_dump())


@router.post("/scale")
def scale_workers(
    request: ScaleWorkersRequest,
    _current_user=Depends(get_current_user),
):
    """Manually scale workers to target number.

    Note: This requires docker-compose access from the API container.
    For production, use Docker Swarm or Kubernetes.
    """
    try:
        # This is for development only
        # In production, use proper orchestration (K8s, Swarm, etc.)
        result = subprocess.run(
            ["docker", "compose", "up", "-d", "--scale", f"worker={request.target_workers}"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Docker command failed: {result.stderr}")

        return {
            "success": True,
            "target_workers": request.target_workers,
            "message": f"Scaling to {request.target_workers} workers",
        }
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Scaling operation timed out",
        ) from exc


@router.post("/autoscale/trigger")
def trigger_autoscale(
    _current_user=Depends(get_current_user),
):
    """Trigger autoscaling check manually.

    Useful for testing or emergency scaling.
    Analyzes current load and scales up/down automatically.
    """
    try:
        service = WorkerAnalyticsService()
        should_scale, target, reason = service.should_autoscale()

        if not should_scale:
            analytics = service.get_analytics()
            return {
                "success": True,
                "action": "no_action",
                "current_workers": analytics["workers"]["total"],
                "target_workers": analytics["workers"]["total"],
                "reason": reason,
                "message": "System is operating normally - no scaling needed",
            }

        # Execute scaling
        result = subprocess.run(
            ["docker", "compose", "up", "-d", "--scale", f"worker={target}"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Docker command failed: {result.stderr}")

        analytics = service.get_analytics()
        return {
            "success": True,
            "action": "scaled",
            "previous_workers": analytics["workers"]["total"],
            "target_workers": target,
            "reason": reason,
            "message": f"Autoscaling executed: {analytics['workers']['total']} → {target} workers",
        }

    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Autoscaling operation timed out",
        ) from exc
    except Exception as e:  # noqa: BLE001 (blind exception)
        logger.error("Failed to scale workers: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to scale workers. This feature requires docker-compose access.",
        ) from e
