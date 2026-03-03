"""Schemas for worker analytics and management."""

from typing import Literal

from pydantic import BaseModel, Field


class QueueStats(BaseModel):
    """Statistics for a single queue."""

    name: str
    pending: int


class WorkerInfo(BaseModel):
    """Information about a single worker."""

    name: str
    state: str
    queues: list[str]
    current_job: str | None
    is_busy: bool


class WorkerStats(BaseModel):
    """Statistics about all workers."""

    total: int
    busy: int
    idle: int
    workers: list[WorkerInfo]


class AutoscalingRecommendation(BaseModel):
    """Autoscaling recommendation."""

    action: Literal["scale_up", "scale_down", "maintain"]
    target_workers: int
    reason: str


class WorkerAnalytics(BaseModel):
    """Complete worker analytics."""

    timestamp: str
    queues: dict[str, QueueStats]
    workers: WorkerStats
    summary: dict[str, int | float]
    autoscaling: AutoscalingRecommendation


class AutoscalingConfig(BaseModel):
    """Autoscaling configuration."""

    min_workers: int = Field(default=2, ge=1, description="Minimum workers")
    max_workers: int = Field(default=5, ge=1, description="Maximum workers")
    scale_up_threshold: int = Field(default=5, ge=1, description="Jobs per worker to scale up")
    scale_down_threshold: int = Field(default=0, ge=0, description="Jobs to scale down")
    idle_time_threshold: int = Field(default=300, ge=60, description="Seconds idle before scale down")


class ScaleWorkersRequest(BaseModel):
    """Request to scale workers."""

    target_workers: int = Field(ge=1, le=10, description="Target number of workers")
