"""Unit tests for session management endpoints.

FASE 3: Tests for listing, revoking, and managing user sessions.
"""

import pytest
from datetime import UTC, datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from robbot.adapters.repositories.auth_session_repository import AuthSessionRepository
from robbot.adapters.repositories.user_repository import UserRepository
from robbot.infra.db.models.user_model import UserModel
from robbot.infra.db.models.auth_session_model import AuthSessionModel
from robbot.infra.db.base import Base


@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    
    # Create tables manually to avoid JSONB issues with SQLite
    with engine.connect() as conn:
        # Create users table
        conn.execute(text("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                is_active BOOLEAN DEFAULT 1 NOT NULL,
                role VARCHAR(50) DEFAULT 'user' NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create auth_sessions table
        conn.execute(text("""
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
        """))
        conn.commit()
    
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def user_repo(db_session):
    """Create UserRepository fixture."""
    return UserRepository(db_session)


@pytest.fixture
def session_repo(db_session):
    """Create AuthSessionRepository fixture."""
    return AuthSessionRepository(db_session)


@pytest.fixture
def test_user(user_repo, db_session):
    """Create test user."""
    user = UserModel(
        email="test@example.com",
        hashed_password="hashed_password_123",
        full_name="Test User",
        is_active=True,
        role="user",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_list_all_sessions_for_user(session_repo, test_user):
    """Test listing all sessions (active + revoked) for a user."""
    # Create 3 sessions: 2 active, 1 revoked
    expires = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=30)
    
    session1 = session_repo.create(
        user_id=test_user.id,
        refresh_token_jti="jti_1",
        ip_address="192.168.1.1",
        user_agent="Chrome/100",
        device_name="Chrome on Windows",
        expires_at=expires,
    )
    
    session2 = session_repo.create(
        user_id=test_user.id,
        refresh_token_jti="jti_2",
        ip_address="192.168.1.2",
        user_agent="Firefox/90",
        device_name="Firefox on Mac",
        expires_at=expires,
    )
    
    session3 = session_repo.create(
        user_id=test_user.id,
        refresh_token_jti="jti_3",
        ip_address="192.168.1.3",
        user_agent="Safari/15",
        device_name="Safari on iPhone",
        expires_at=expires,
    )
    
    # Revoke session3
    session_repo.revoke(session3, reason="test_revocation")
    
    # List all sessions
    sessions = session_repo.get_all_by_user_id(test_user.id)
    
    assert len(sessions) == 3
    
    # Check active sessions
    active_sessions = [s for s in sessions if not s.is_revoked]
    assert len(active_sessions) == 2
    
    # Check revoked sessions
    revoked_sessions = [s for s in sessions if s.is_revoked]
    assert len(revoked_sessions) == 1
    assert revoked_sessions[0].revocation_reason == "test_revocation"


def test_revoke_session_by_id(session_repo, test_user):
    """Test revoking a specific session by ID."""
    expires = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=30)
    
    session = session_repo.create(
        user_id=test_user.id,
        refresh_token_jti="jti_test",
        ip_address="192.168.1.1",
        user_agent="Chrome/100",
        device_name="Chrome on Windows",
        expires_at=expires,
    )
    
    assert not session.is_revoked
    
    # Revoke by ID
    success = session_repo.revoke_by_id(
        session_id=session.id,
        user_id=test_user.id,
        reason="manual_revocation"
    )
    
    assert success
    
    # Verify revocation
    revoked_session = session_repo.get_by_id(session.id)
    assert revoked_session.is_revoked
    assert revoked_session.revocation_reason == "manual_revocation"
    assert revoked_session.revoked_at is not None


def test_revoke_session_by_id_wrong_user(session_repo, test_user, db_session):
    """Test that revoking a session fails if user_id doesn't match."""
    # Create another user
    other_user = UserModel(
        email="other@example.com",
        hashed_password="hashed_password_456",
        full_name="Other User",
        is_active=True,
        role="user",
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)
    
    expires = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=30)
    
    # Create session for test_user
    session = session_repo.create(
        user_id=test_user.id,
        refresh_token_jti="jti_test",
        ip_address="192.168.1.1",
        user_agent="Chrome/100",
        device_name="Chrome on Windows",
        expires_at=expires,
    )
    
    # Try to revoke with other_user's ID (should fail)
    success = session_repo.revoke_by_id(
        session_id=session.id,
        user_id=other_user.id,
        reason="unauthorized_attempt"
    )
    
    assert not success
    
    # Verify session is still active
    unchanged_session = session_repo.get_by_id(session.id)
    assert not unchanged_session.is_revoked


def test_revoke_all_sessions_for_user(session_repo, test_user):
    """Test revoking all sessions for a user."""
    expires = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=30)
    
    # Create 3 sessions
    for i in range(1, 4):
        session_repo.create(
            user_id=test_user.id,
            refresh_token_jti=f"jti_{i}",
            ip_address=f"192.168.1.{i}",
            user_agent=f"Browser/{i}",
            device_name=f"Device {i}",
            expires_at=expires,
        )
    
    # Revoke all
    count = session_repo.revoke_all_for_user(
        user_id=test_user.id,
        reason="revoke_all_test"
    )
    
    assert count == 3
    
    # Verify all sessions are revoked
    sessions = session_repo.get_all_by_user_id(test_user.id)
    assert all(s.is_revoked for s in sessions)
    assert all(s.revocation_reason == "revoke_all_test" for s in sessions)


def test_get_active_sessions_excludes_expired_and_revoked(session_repo, test_user):
    """Test that get_active_by_user_id excludes expired and revoked sessions."""
    now = datetime.now(UTC).replace(tzinfo=None)
    
    # Create active session
    active_session = session_repo.create(
        user_id=test_user.id,
        refresh_token_jti="jti_active",
        ip_address="192.168.1.1",
        user_agent="Chrome/100",
        device_name="Chrome",
        expires_at=now + timedelta(minutes=30),
    )
    
    # Create expired session
    expired_session = session_repo.create(
        user_id=test_user.id,
        refresh_token_jti="jti_expired",
        ip_address="192.168.1.2",
        user_agent="Firefox/90",
        device_name="Firefox",
        expires_at=now - timedelta(minutes=10),  # Already expired
    )
    
    # Create revoked session
    revoked_session = session_repo.create(
        user_id=test_user.id,
        refresh_token_jti="jti_revoked",
        ip_address="192.168.1.3",
        user_agent="Safari/15",
        device_name="Safari",
        expires_at=now + timedelta(minutes=30),
    )
    session_repo.revoke(revoked_session, reason="test")
    
    # Get active sessions
    active_sessions = session_repo.get_active_by_user_id(test_user.id)
    
    # Should only return the active, non-expired session
    assert len(active_sessions) == 1
    assert active_sessions[0].refresh_token_jti == "jti_active"
