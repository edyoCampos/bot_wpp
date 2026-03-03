"""Service for worker analytics and autoscaling."""

import logging
import os
from datetime import datetime

from redis import Redis
from rq import Queue, Worker

from robbot.infra.redis.client import get_redis_client

logger = logging.getLogger(__name__)


class WorkerAnalyticsService:
    """Service for monitoring workers and implementing autoscaling."""

    def __init__(self, redis_client: Redis | None = None):
        self.redis = redis_client or get_redis_client()
        # Defaults
        default_min = 2
        default_max = 5
        default_up_threshold = 5
        default_down_threshold = 0
        default_idle_seconds = 300

        # Allow configuration via environment variables
        self.min_workers = int(os.getenv("AUTOSCALER_MIN_WORKERS", str(default_min)))
        self.max_workers = int(os.getenv("AUTOSCALER_MAX_WORKERS", str(default_max)))
        self.scale_up_threshold = int(os.getenv("AUTOSCALER_SCALE_UP_THRESHOLD", str(default_up_threshold)))
        self.scale_down_threshold = int(os.getenv("AUTOSCALER_SCALE_DOWN_THRESHOLD", str(default_down_threshold)))
        self.idle_time_threshold = int(os.getenv("AUTOSCALER_IDLE_TIME_THRESHOLD", str(default_idle_seconds)))

    def get_queue_stats(self) -> dict[str, dict]:
        """Get statistics for all queues."""
        queue_names = ["messages", "ai", "escalation", "failed"]
        stats = {}

        for name in queue_names:
            queue = Queue(name, connection=self.redis)
            stats[name] = {
                "pending": queue.count,
                "name": name,
            }

        return stats

    def get_worker_stats(self) -> dict:
        """Get statistics about active workers."""
        workers = Worker.all(connection=self.redis)

        worker_list = []
        busy_count = 0
        idle_count = 0

        for worker in workers:
            is_busy = worker.state != "idle"
            if is_busy:
                busy_count += 1
            else:
                idle_count += 1

            worker_list.append(
                {
                    "name": worker.name,
                    "state": worker.state,
                    "queues": [q.name for q in worker.queues],
                    "current_job": worker.get_current_job_id(),
                    "is_busy": is_busy,
                }
            )

        return {
            "total": len(workers),
            "busy": busy_count,
            "idle": idle_count,
            "workers": worker_list,
        }

    def get_analytics(self) -> dict:
        """Get complete analytics dashboard data."""
        queue_stats = self.get_queue_stats()
        worker_stats = self.get_worker_stats()

        # Calculate total pending jobs (exclude failed queue)
        total_pending = sum([queue_stats[name]["pending"] for name in ["messages", "ai", "escalation"]])

        # Get historical stats
        processed = int(self.redis.get("rq:stat:processed") or 0)
        failed = int(self.redis.get("rq:stat:failed") or 0)

        # Calculate autoscaling recommendation
        recommendation = self._calculate_autoscaling_recommendation(
            total_pending, worker_stats["total"], worker_stats["idle"]
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "queues": queue_stats,
            "workers": worker_stats,
            "summary": {
                "total_pending": total_pending,
                "total_processed": processed,
                "total_failed": failed,
                "success_rate": round((processed / (processed + failed) * 100) if (processed + failed) > 0 else 100, 2),
            },
            "autoscaling": recommendation,
        }

    def _calculate_autoscaling_recommendation(self, pending: int, workers: int, idle: int) -> dict:
        """Calculate autoscaling recommendation."""
        # Always enforce minimum number of workers
        if workers < self.min_workers:
            return {
                "action": "scale_up",
                "target_workers": self.min_workers,
                "reason": "Below minimum workers",
            }

        jobs_per_worker = pending / workers if workers > 0 else 0

        # Scale up if too many jobs per worker
        if jobs_per_worker > self.scale_up_threshold and workers < self.max_workers:
            target = min(workers + 1, self.max_workers)
            return {
                "action": "scale_up",
                "target_workers": target,
                "reason": f"High load: {jobs_per_worker:.1f} jobs/worker (threshold: {self.scale_up_threshold})",
            }

        # Scale down if all idle and above minimum
        if pending == 0 and idle == workers and workers > self.min_workers:
            target = max(workers - 1, self.min_workers)
            return {
                "action": "scale_down",
                "target_workers": target,
                "reason": "All workers idle with no pending jobs",
            }

        return {
            "action": "maintain",
            "target_workers": workers,
            "reason": "System operating normally",
        }

    def should_autoscale(self) -> tuple[bool, int, str]:
        """Check if autoscaling should be triggered.

        Returns:
            Tuple of (should_scale, target_workers, reason)
        """
        analytics = self.get_analytics()
        recommendation = analytics["autoscaling"]

        should_scale = recommendation["action"] != "maintain"
        target = recommendation["target_workers"]
        reason = recommendation["reason"]

        return should_scale, target, reason

    def get_autoscaling_config(self) -> dict:
        """Get current autoscaling configuration."""
        return {
            "min_workers": self.min_workers,
            "max_workers": self.max_workers,
            "scale_up_threshold": self.scale_up_threshold,
            "scale_down_threshold": self.scale_down_threshold,
            "idle_time_threshold": self.idle_time_threshold,
        }

    def update_autoscaling_config(self, config: dict) -> dict:
        """Update autoscaling configuration."""
        if "min_workers" in config:
            self.min_workers = max(1, config["min_workers"])
        if "max_workers" in config:
            self.max_workers = max(self.min_workers, config["max_workers"])
        if "scale_up_threshold" in config:
            self.scale_up_threshold = max(1, config["scale_up_threshold"])

        return self.get_autoscaling_config()
