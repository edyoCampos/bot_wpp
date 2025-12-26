"""Repository for webhook log persistence."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from robbot.infra.db.models.webhook_log_model import WebhookLog


class WebhookLogRepository:
    """Data access layer for webhook logs."""

    def __init__(self, db: Session):
        """Initialize repository with database session.

        Args:
            db: SQLAlchemy session
        """
        self.db = db

    def create(
        self,
        session_name: str,
        event_type: str,
        payload: dict,
    ) -> WebhookLog:
        """Create webhook log entry.

        Args:
            session_name: Session name
            event_type: Event type (message, message.ack, etc.)
            payload: Full webhook payload

        Returns:
            Created log
        """
        log = WebhookLog(
            session_name=session_name,
            event_type=event_type,
            payload=payload,
            processed=False,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def mark_processed(self, log_id: int, error: str | None = None) -> None:
        """Mark webhook log as processed.

        Args:
            log_id: Log ID
            error: Error message if processing failed
        """
        log = self.db.get(WebhookLog, log_id)
        if log:
            log.processed = True
            if error:
                log.error = error
            self.db.commit()

    def get_unprocessed(
        self,
        limit: int = 100,
        event_type: str | None = None,
    ) -> list[WebhookLog]:
        """Get unprocessed webhook logs.

        Args:
            limit: Max number of logs to return
            event_type: Filter by event type

        Returns:
            List of unprocessed logs
        """
        stmt = (
            select(WebhookLog)
            .where(WebhookLog.processed == False)
            .order_by(WebhookLog.created_at.asc())
            .limit(limit)
        )

        if event_type:
            stmt = stmt.where(WebhookLog.event_type == event_type)

        return list(self.db.scalars(stmt).all())

    def cleanup_old_logs(self, days: int = 30) -> int:
        """Delete processed logs older than specified days.

        Args:
            days: Number of days to keep

        Returns:
            Number of deleted logs
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        stmt = (
            select(WebhookLog)
            .where(WebhookLog.processed == True)
            .where(WebhookLog.created_at < cutoff_date)
        )
        logs = list(self.db.scalars(stmt).all())

        for log in logs:
            self.db.delete(log)

        self.db.commit()
        return len(logs)
