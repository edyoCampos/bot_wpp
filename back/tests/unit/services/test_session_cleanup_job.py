"""Unit tests for SessionCleanupJob.

Tests the background job that deletes expired authentication sessions.
"""
# pylint: disable=abstract-class-instantiated,redefined-outer-name,unused-argument

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from robbot.infra.persistence.repositories.auth_session_repository import AuthSessionRepository
from robbot.infra.persistence.models.user_model import UserModel
from robbot.infra.jobs.session_cleanup_job import SessionCleanupJob


@pytest.fixture
def db_session_instance():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")

    # Create tables manually
    with engine.connect() as conn:
        # Create users table
        conn.execute(
            text("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                full_name VARCHAR(255),
                is_active BOOLEAN DEFAULT 1 NOT NULL,
                role VARCHAR(50) DEFAULT 'user' NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        )

        # Create auth_sessions table
        conn.execute(
            text("""
            CREATE TABLE auth_sessions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                refresh_token_jti VARCHAR(255) UNIQUE NOT NULL,
                device_name VARCHAR(255),
                ip_address VARCHAR(45) NOT NULL,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                is_revoked BOOLEAN DEFAULT 0 NOT NULL,
                revoked_at TIMESTAMP,
                revocation_reason VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        )
        conn.commit()

    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session):
    """Create test user."""
    user = UserModel(
        email="cleanup@example.com",
        full_name="Cleanup Test User",
        is_active=True,
        role="user",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def mock_sync_session(db_session):
    """Mock get_sync_session to return the test database session."""
    with patch("robbot.infra.jobs.session_cleanup_job.get_sync_session") as mock:
        mock.return_value.__enter__.return_value = db_session
        mock.return_value.__exit__.return_value = None
        yield mock


def test_cleanup_deletes_old_expired_sessions(db_session, test_user, mock_sync_session):
    """Test that cleanup deletes sessions expired more than retention_days ago."""
    repo = AuthSessionRepository(db_session)
    now = datetime.now(UTC).replace(tzinfo=None)

    # Create session expired 40 days ago (should be deleted)
    repo.create(
        user_id=test_user.id,
        refresh_token_jti="jti_old_expired",
        ip_address="192.168.1.1",
        user_agent="Chrome/100",
        device_name="Chrome on Windows",
        expires_at=now - timedelta(days=40),
    )

    # Create session expired 20 days ago (should be kept - within retention)
    repo.create(
        user_id=test_user.id,
        refresh_token_jti="jti_recent_expired",
        ip_address="192.168.1.2",
        user_agent="Firefox/90",
        device_name="Firefox on Mac",
        expires_at=now - timedelta(days=20),
    )

    # Create active session (should be kept)
    repo.create(
        user_id=test_user.id,
        refresh_token_jti="jti_active",
        ip_address="192.168.1.3",
        user_agent="Safari/15",
        device_name="Safari on iPhone",
        expires_at=now + timedelta(days=7),
    )

    # Run cleanup with 30 days retention
    job = SessionCleanupJob(retention_days=30)
    job.run()

    # Verify results
    all_sessions = repo.get_all_by_user_id(test_user.id)
    assert len(all_sessions) == 2  # Only recent expired and active remain

    jtis = [s.refresh_token_jti for s in all_sessions]
    assert "jti_old_expired" not in jtis  # Deleted
    assert "jti_recent_expired" in jtis  # Kept
    assert "jti_active" in jtis  # Kept


def test_cleanup_does_not_delete_recent_sessions(db_session, test_user, mock_sync_session):
    """Test that cleanup preserves sessions expired within retention period."""
    repo = AuthSessionRepository(db_session)
    now = datetime.now(UTC).replace(tzinfo=None)

    # Create 5 sessions expired 10 days ago (all within 30-day retention)
    for i in range(5):
        repo.create(
            user_id=test_user.id,
            refresh_token_jti=f"jti_{i}",
            ip_address=f"192.168.1.{i}",
            user_agent=f"Browser/{i}",
            device_name=f"Device {i}",
            expires_at=now - timedelta(days=10),
        )

    # Run cleanup
    job = SessionCleanupJob(retention_days=30)
    job.run()

    # Verify all sessions are kept
    all_sessions = repo.get_all_by_user_id(test_user.id)
    assert len(all_sessions) == 5


def test_cleanup_with_custom_retention(db_session, test_user, mock_sync_session):
    """Test cleanup with different retention periods."""
    repo = AuthSessionRepository(db_session)
    now = datetime.now(UTC).replace(tzinfo=None)

    # Create session expired 15 days ago
    repo.create(
        user_id=test_user.id,
        refresh_token_jti="jti_15_days",
        ip_address="192.168.1.1",
        user_agent="Chrome/100",
        device_name="Chrome on Windows",
        expires_at=now - timedelta(days=15),
    )

    # Run cleanup with 10-day retention (should delete the session)
    job = SessionCleanupJob(retention_days=10)
    job.run()

    # Verify session was deleted
    all_sessions = repo.get_all_by_user_id(test_user.id)
    assert len(all_sessions) == 0


def test_cleanup_handles_empty_table(db_session, mock_sync_session):
    """Test that cleanup handles empty auth_sessions table gracefully."""
    job = SessionCleanupJob(retention_days=30)
    # Should not raise exception
    job.run()


def test_cleanup_returns_deleted_count(db_session, test_user, mock_sync_session):
    """Test that cleanup job logs the number of deleted sessions."""
    repo = AuthSessionRepository(db_session)
    now = datetime.now(UTC).replace(tzinfo=None)

    # Create 3 old expired sessions
    for i in range(3):
        repo.create(
            user_id=test_user.id,
            refresh_token_jti=f"jti_old_{i}",
            ip_address=f"192.168.1.{i}",
            user_agent=f"Browser/{i}",
            device_name=f"Device {i}",
            expires_at=now - timedelta(days=40),
        )

    # Run cleanup and verify deletion count
    # Note: We can't easily verify the count here without modifying the job
    # to return it, but the test confirms no exceptions are raised
    job = SessionCleanupJob(retention_days=30)
    job.run()

    # Verify all were deleted
    all_sessions = repo.get_all_by_user_id(test_user.id)
    assert len(all_sessions) == 0

