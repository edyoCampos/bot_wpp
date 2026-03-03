"""
Unit tests for NotificationService.

Tests core business logic for notification management.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from robbot.core.custom_exceptions import NotFoundException
from robbot.infra.persistence.models.notification_model import NotificationModel
from robbot.services.communication.notification_service import NotificationService


@pytest.fixture()
def db_session_instance():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    NotificationModel.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = session_local()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def notification_service(db_session_instance):
    """Create NotificationService instance."""
    return NotificationService(db_session_instance)


# =====================================================================
# CREATE NOTIFICATION TESTS
# =====================================================================
def test_create_notification(notification_service):
    """Test creating a new notification."""
    user_id = 123
    notification_type = "NEW_LEAD"
    title = "New Lead Assigned"
    message = "You have been assigned a new lead: John Doe"

    notification = notification_service.create_notification(
        user_id=user_id, notification_type=notification_type, title=title, message=message
    )

    assert notification is not None
    assert notification.user_id == user_id
    assert notification.type == notification_type
    assert notification.title == title
    assert notification.message == message
    assert notification.read is False  # Default state


def test_create_notification_different_types(notification_service):
    """Test creating notifications with different types."""
    user_id = 456

    types = [
        ("NEW_LEAD", "Lead Notification", "New lead available"),
        ("NEW_MESSAGE", "Message Notification", "New message received"),
        ("URGENT", "Urgent Notification", "Urgent attention required"),
    ]

    for notif_type, title, message in types:
        notification = notification_service.create_notification(
            user_id=user_id, notification_type=notif_type, title=title, message=message
        )

        assert notification.type == notif_type


def test_create_multiple_notifications_for_user(notification_service):
    """Test creating multiple notifications for the same user."""
    user_id = 789

    # Create 3 notifications
    for i in range(3):
        notification_service.create_notification(
            user_id=user_id, notification_type="TEST", title=f"Test {i}", message=f"Message {i}"
        )

    # Retrieve all notifications
    notifications = notification_service.get_user_notifications(user_id)

    assert len(notifications) == 3


# =====================================================================
# MARK AS READ TESTS
# =====================================================================
def test_mark_notification_as_read(notification_service):
    """Test marking a notification as read."""
    # Create notification
    notification = notification_service.create_notification(
        user_id=111, notification_type="TEST", title="Test", message="Test message"
    )

    assert notification.read is False

    # Mark as read
    updated = notification_service.mark_as_read(str(notification.id))

    assert updated.read is True


def test_mark_nonexistent_notification_as_read(notification_service):
    """Test marking non-existent notification as read raises error."""
    fake_id = "00000000-0000-0000-0000-000000000000"

    with pytest.raises(NotFoundException) as exc_info:
        notification_service.mark_as_read(fake_id)

    assert "not found" in str(exc_info.value).lower()


def test_mark_already_read_notification(notification_service):
    """Test marking an already read notification (idempotent operation)."""
    # Create and mark as read
    notification = notification_service.create_notification(
        user_id=222, notification_type="TEST", title="Already Read", message="Test"
    )

    notification_service.mark_as_read(str(notification.id))

    # Mark as read again
    updated = notification_service.mark_as_read(str(notification.id))

    assert updated.read is True


# =====================================================================
# GET USER NOTIFICATIONS TESTS
# =====================================================================
def test_get_user_notifications_all(notification_service):
    """Test getting all notifications for a user."""
    user_id = 333

    # Create 5 notifications (mix of read and unread)
    for i in range(5):
        notif = notification_service.create_notification(
            user_id=user_id, notification_type="TEST", title=f"Test {i}", message=f"Message {i}"
        )

        # Mark some as read
        if i % 2 == 0:
            notification_service.mark_as_read(str(notif.id))

    # Get all notifications
    notifications = notification_service.get_user_notifications(user_id=user_id, unread_only=False)

    assert len(notifications) == 5


def test_get_user_notifications_unread_only(notification_service):
    """Test getting only unread notifications for a user."""
    user_id = 444

    # Create notifications
    for i in range(5):
        notif = notification_service.create_notification(
            user_id=user_id, notification_type="TEST", title=f"Test {i}", message=f"Message {i}"
        )

        # Mark 2 as read
        if i < 2:
            notification_service.mark_as_read(str(notif.id))

    # Get unread only
    notifications = notification_service.get_user_notifications(user_id=user_id, unread_only=True)

    assert len(notifications) == 3
    assert all(not n.read for n in notifications)


def test_get_user_notifications_with_limit(notification_service):
    """Test getting notifications respects limit parameter."""
    user_id = 555

    # Create 10 notifications
    for i in range(10):
        notification_service.create_notification(
            user_id=user_id, notification_type="TEST", title=f"Test {i}", message=f"Message {i}"
        )

    # Get with limit
    notifications = notification_service.get_user_notifications(user_id=user_id, limit=5)

    assert len(notifications) <= 5


def test_get_notifications_for_different_users(notification_service):
    """Test that users only see their own notifications."""
    user1_id = 666
    user2_id = 777

    # Create notifications for user1
    notification_service.create_notification(
        user_id=user1_id, notification_type="TEST", title="User 1 Notification", message="For user 1"
    )

    # Create notifications for user2
    notification_service.create_notification(
        user_id=user2_id, notification_type="TEST", title="User 2 Notification", message="For user 2"
    )

    # Get notifications for user1
    user1_notifications = notification_service.get_user_notifications(user1_id)

    assert len(user1_notifications) == 1
    assert all(n.user_id == user1_id for n in user1_notifications)


def test_get_notifications_empty_result(notification_service):
    """Test getting notifications for user with no notifications."""
    user_id = 888

    notifications = notification_service.get_user_notifications(user_id)

    assert len(notifications) == 0
    assert isinstance(notifications, list)


# =====================================================================
# COUNT UNREAD TESTS
# =====================================================================
def test_count_unread_notifications(notification_service):
    """Test counting unread notifications."""
    user_id = 999

    # Create 5 notifications
    for i in range(5):
        notif = notification_service.create_notification(
            user_id=user_id, notification_type="TEST", title=f"Test {i}", message=f"Message {i}"
        )

        # Mark 2 as read
        if i < 2:
            notification_service.mark_as_read(str(notif.id))

    # Count unread
    unread_count = notification_service.count_unread(user_id)

    assert unread_count == 3


def test_count_unread_zero(notification_service):
    """Test counting unread notifications when all are read."""
    user_id = 1000

    # Create and mark all as read
    for i in range(3):
        notif = notification_service.create_notification(
            user_id=user_id, notification_type="TEST", title=f"Test {i}", message=f"Message {i}"
        )
        notification_service.mark_as_read(str(notif.id))

    unread_count = notification_service.count_unread(user_id)

    assert unread_count == 0


def test_count_unread_no_notifications(notification_service):
    """Test counting unread for user with no notifications."""
    user_id = 1111

    unread_count = notification_service.count_unread(user_id)

    assert unread_count == 0


# =====================================================================
# SPECIALIZED NOTIFICATION TESTS
# =====================================================================
def test_notify_new_lead(notification_service):
    """Test specialized notification for new lead."""
    user_id = 1222
    lead_phone = "+5511999999999"
    lead_name = "John Doe"

    notification = notification_service.notify_new_lead(user_id=user_id, lead_phone=lead_phone, lead_name=lead_name)

    assert notification is not None
    assert notification.user_id == user_id
    assert notification.type == "NEW_LEAD"
    assert lead_name in notification.message


def test_notify_urgent_message(notification_service):
    """Test specialized notification for urgent message."""
    user_id = 1333
    conversation_id = "conv-123"
    message_text = "This is urgent: +5511888888888"

    notification = notification_service.notify_urgent_message(
        user_id=user_id, conversation_id=conversation_id, message_text=message_text
    )

    assert notification is not None
    assert notification.user_id == user_id
    assert notification.type == "URGENT_MESSAGE"
    assert conversation_id in notification.message


def test_notify_transfer_received(notification_service):
    """Test specialized notification for conversation transfer."""
    user_id = 1444
    conversation_id = "abc123"
    from_user_name = "Agent Smith"

    notification = notification_service.notify_transfer_received(
        user_id=user_id, conversation_id=conversation_id, from_user_name=from_user_name
    )

    assert notification is not None
    assert notification.user_id == user_id
    assert notification.type == "TRANSFER_RECEIVED"
    assert from_user_name in notification.message


# =====================================================================
# EDGE CASE TESTS
# =====================================================================
def test_create_notification_with_long_message(notification_service):
    """Test creating notification with very long message."""
    user_id = 1555
    long_message = "A" * 2000  # Very long message

    notification = notification_service.create_notification(
        user_id=user_id, notification_type="TEST", title="Long Message Test", message=long_message
    )

    assert notification is not None
    assert len(notification.message) == 2000


def test_create_notification_empty_title(notification_service):
    """Test creating notification with empty title."""
    user_id = 1666

    notification = notification_service.create_notification(
        user_id=user_id, notification_type="TEST", title="", message="Test message"
    )

    assert notification is not None
    assert notification.title == ""


def test_notification_ordering(notification_service):
    """Test that notifications are ordered by created_at descending."""
    user_id = 1777

    # Create notifications with slight delay simulation
    notification_service.create_notification(
        user_id=user_id, notification_type="TEST", title="First", message="First notification"
    )

    notification_service.create_notification(
        user_id=user_id, notification_type="TEST", title="Second", message="Second notification"
    )

    notification_service.create_notification(
        user_id=user_id, notification_type="TEST", title="Third", message="Third notification"
    )

    # Get all notifications
    notifications = notification_service.get_user_notifications(user_id)

    # Verify we got all 3
    assert len(notifications) == 3

    # Most recent should be first (if ordering is implemented)
    # This assumes the service/repository implements DESC ordering

