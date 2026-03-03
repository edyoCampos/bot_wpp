"""
Notification Service - In-app notification management.

Business logic for creating and managing user notifications.
"""

import logging

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.notification_repository import NotificationRepository
from robbot.core.custom_exceptions import NotFoundException
from robbot.infra.persistence.models.notification_model import NotificationModel

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for managing in-app notifications.

    Responsibilities:
    - Create notifications for users
    - Mark notifications as read
    - List user notifications
    - Send specialized notifications (new lead, urgent message, etc.)
    """

    def __init__(self, db: Session):
        """
        Initialize service with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.repo = NotificationRepository(db)

    def create_notification(
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
            notification_type: Type of notification (NEW_LEAD, NEW_MESSAGE, etc.)
            title: Notification title
            message: Detailed message content

        Returns:
            Created notification model
        """
        notification = self.repo.create(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
        )

        logger.info(
            f"[SUCCESS] Notification created (id={notification.id}, user_id={user_id}, type={notification_type})"
        )

        return notification

    def mark_as_read(self, notification_id: str) -> NotificationModel:
        """
        Mark notification as read.

        Args:
            notification_id: UUID of the notification

        Returns:
            Updated notification model

        Raises:
            NotFoundException: If notification does not exist
        """
        notification = self.repo.mark_as_read(notification_id)

        if not notification:
            raise NotFoundException(f"Notification {notification_id} not found")

        logger.info("[SUCCESS] Notification marked as read (id=%s)", notification_id)

        return notification

    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[NotificationModel]:
        """
        Get notifications for a user.

        Args:
            user_id: ID of the user
            unread_only: Return only unread notifications
            limit: Maximum number of results

        Returns:
            List of notification models ordered by created_at desc
        """
        notifications = self.repo.get_by_user(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit,
        )

        logger.info(
            f"[SUCCESS] Notifications retrieved (user_id={user_id}, "
            f"count={len(notifications)}, unread_only={unread_only})"
        )

        return notifications

    def count_unread(self, user_id: int) -> int:
        """
        Count unread notifications for a user.

        Args:
            user_id: ID of the user

        Returns:
            Count of unread notifications
        """
        return self.repo.count_unread(user_id)

    def notify_new_lead(
        self,
        user_id: int,
        lead_phone: str,
        lead_name: str,
    ) -> NotificationModel:
        """
        Notify user about new lead assignment.

        Args:
            user_id: ID of the secretary/agent
            lead_phone: Lead's phone number
            lead_name: Lead's name

        Returns:
            Created notification model
        """
        return self.create_notification(
            user_id=user_id,
            notification_type="NEW_LEAD",
            title="New Lead Assigned",
            message=f"New lead: {lead_name} ({lead_phone})",
        )

    def notify_new_message(
        self,
        user_id: int,
        conversation_id: str,
        message_preview: str,
    ) -> NotificationModel:
        """
        Notify user about new message in conversation.

        Args:
            user_id: ID of the secretary/agent
            conversation_id: UUID of the conversation
            message_preview: Preview text of the message

        Returns:
            Created notification model
        """
        return self.create_notification(
            user_id=user_id,
            notification_type="NEW_MESSAGE",
            title="New Message",
            message=f"Conversation {conversation_id[:8]}: {message_preview[:50]}...",
        )

    def notify_urgent_message(
        self,
        user_id: int,
        conversation_id: str,
        message_text: str,
    ) -> NotificationModel:
        """
        Notify user about urgent message requiring immediate attention.

        Args:
            user_id: ID of the secretary/agent
            conversation_id: UUID of the conversation
            message_text: Text of the urgent message

        Returns:
            Created notification model
        """
        return self.create_notification(
            user_id=user_id,
            notification_type="URGENT_MESSAGE",
            title="[WARNING] Urgent Message",
            message=f"[URGENT] Conversation {conversation_id[:8]}: {message_text[:100]}",
        )

    def notify_transfer_received(
        self,
        user_id: int,
        conversation_id: str,
        from_user_name: str,
    ) -> NotificationModel:
        """
        Notify user about receiving a transferred conversation.

        Args:
            user_id: ID of the receiving user
            conversation_id: UUID of the conversation
            from_user_name: Name of the user who transferred

        Returns:
            Created notification model
        """
        return self.create_notification(
            user_id=user_id,
            notification_type="TRANSFER_RECEIVED",
            title="Conversation Transferred",
            message=f"You received a conversation from {from_user_name} (ID: {conversation_id[:8]})",
        )

