"""Background job to cleanup expired authentication sessions.

This job deletes expired sessions from the database to prevent table bloat
and maintain optimal query performance.
"""

import logging
from datetime import UTC, datetime, timedelta

from robbot.infra.persistence.repositories.auth_session_repository import AuthSessionRepository
from robbot.infra.db.session import get_sync_session
from robbot.infra.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class SessionCleanupJob(BaseJob):
    """Job to delete expired authentication sessions from database.

    Runs daily to remove sessions that expired more than 30 days ago.
    Keeps recent expired sessions for audit purposes.
    """

    def __init__(self, retention_days: int = 30):
        """Initialize session cleanup job.

        Args:
            retention_days: Number of days to retain expired sessions (default: 30)
        """
        super().__init__()
        self.retention_days = retention_days

    def execute(self) -> int:
        """Execute session cleanup (implements BaseJob.execute()).

        Deletes all sessions that expired more than retention_days ago.

        Returns:
            Number of sessions deleted
        """
        logger.info(
            "[INFO] Starting session cleanup (retention: %d days)",
            self.retention_days,
        )

        with get_sync_session() as db:
            repo = AuthSessionRepository(db)
            cutoff_date = datetime.now(UTC) - timedelta(days=self.retention_days)
            deleted_count = repo.delete_expired(before=cutoff_date)

            logger.info(
                "[SUCCESS] Session cleanup completed: %d sessions deleted",
                deleted_count,
            )
            return deleted_count

    def run(self) -> None:
        """Execute session cleanup (legacy method, calls execute()).

        Deletes all sessions that expired more than retention_days ago.
        Logs the number of sessions deleted.
        """
        logger.info("[INFO] Starting session cleanup job (retention: %d days)", self.retention_days)

        try:
            with get_sync_session() as db:
                repo = AuthSessionRepository(db)

                # Calculate cutoff date: delete sessions expired before this date
                cutoff_date = datetime.now(UTC) - timedelta(days=self.retention_days)

                # Delete expired sessions
                deleted_count = repo.delete_expired(before=cutoff_date)

                logger.info(
                    "[SUCCESS] Session cleanup completed: %d expired sessions deleted",
                    deleted_count,
                )

        except Exception as exc:  # noqa: BLE001 (blind exception)
            logger.exception("[ERROR] Session cleanup job failed: %s", exc)
            raise


def run_session_cleanup(retention_days: int = 30) -> None:
    """Standalone function to run session cleanup job.

    This function can be called directly from RQ scheduler or cron.

    Args:
        retention_days: Number of days to retain expired sessions (default: 30)
    """
    job = SessionCleanupJob(retention_days=retention_days)
    job.run()

