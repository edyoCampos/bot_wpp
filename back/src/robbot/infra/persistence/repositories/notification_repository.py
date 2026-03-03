"""
Notification Repository - Data access layer for notifications.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.base_repository import BaseRepository
from robbot.infra.persistence.models.notification_model import NotificationModel


class NotificationRepository(BaseRepository[NotificationModel]):
    """
    Repository for notification data access.

    Encapsulates all database operations related to notifications.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        super().__init__(db, NotificationModel)

    def create(  # pylint: disable=arguments-differ
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
    ) -> NotificationModel:
        """
        Create a new notification.

        Args:
            user_id: ID of the user to notify
            notification_type: Type of notification
            title: Notification title
            message: Notification message

        Returns:
            Created notification model
        """
        notification = NotificationModel(
            user_id=user_id, type=notification_type, title=title, message=message, read=False
        )
        self.db.add(notification)
        self.db.flush()
        self.db.refresh(notification)
        return notification

    def get_by_user(self, user_id: int, unread_only: bool = False, limit: int = 50) -> list[NotificationModel]:
        """
        Get notifications for a specific user.

        Args:
            user_id: ID of the user
            unread_only: If True, return only unread notifications
            limit: Maximum number of notifications to return

        Returns:
            List of notification models ordered by created_at desc
        """
        stmt = (
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
            .limit(limit)
        )

        if unread_only:
            stmt = stmt.where(not NotificationModel.read)

        return list(self.db.scalars(stmt).all())

    def count_unread(self, user_id: int) -> int:
        """
        Count unread notifications for a user.

        Args:
            user_id: ID of the user

        Returns:
            Count of unread notifications
        """
        stmt = select(NotificationModel).where(NotificationModel.user_id == user_id).where(not NotificationModel.read)
        return len(list(self.db.scalars(stmt).all()))

    def mark_as_read(self, notification_id: str) -> NotificationModel | None:
        """
        Mark a notification as read.

        Args:
            notification_id: UUID of the notification

        Returns:
            Updated notification model or None if not found
        """
        notification = self.get_by_id(notification_id)
        if notification:
            notification.read = True
            self.db.flush()
        return notification

    def mark_all_as_read(self, user_id: int) -> int:
        """
        Mark all notifications as read for a user.

        Args:
            user_id: ID of the user

        Returns:
            Count of notifications marked as read
        """
        stmt = select(NotificationModel).where(NotificationModel.user_id == user_id).where(not NotificationModel.read)
        notifications = list(self.db.scalars(stmt).all())

        for notification in notifications:
            notification.read = True

        self.db.flush()
        return len(notifications)

    def delete_old_read(self, user_id: int, days: int = 30) -> int:
        """
        Delete old read notifications for a user.

        Args:
            user_id: ID of the user
            days: Delete notifications older than this many days

        Returns:
            Count of notifications deleted
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=days)

        stmt = (
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .where(NotificationModel.read)
            .where(NotificationModel.created_at < cutoff_date)
        )
        notifications = list(self.db.scalars(stmt).all())

        for notification in notifications:
            self.db.delete(notification)

        self.db.flush()
        return len(notifications)

