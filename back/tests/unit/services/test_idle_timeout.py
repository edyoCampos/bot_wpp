"""Unit tests for idle timeout functionality in session refresh.

Tests that sessions expire after 30 days of inactivity.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session as SQLSession

from robbot.core.custom_exceptions import AuthException
from robbot.schemas.token import Token
from robbot.services.auth.auth_services import AuthService


@pytest.fixture
def auth_service_mock():
    """Create AuthService with mocked database session."""
    # AuthService constructor only accepts db parameter
    # It internally creates all repositories and services
    svc = AuthService(db=MagicMock(spec=SQLSession))
    svc.session_repo = MagicMock()
    svc.token_repo = MagicMock()
    return svc


def test_idle_timeout_revokes_inactive_session(auth_service_mock):
    """Test that sessions inactive for >30 days are revoked."""
    # Create a session that was last used 31 days ago
    old_session = MagicMock()
    old_session.id = 1
    old_session.last_used_at = datetime.now(UTC) - timedelta(days=31)
    old_session.created_at = datetime.now(UTC) - timedelta(days=40)
    old_session.is_revoked = False
    old_session.is_expired = False

    auth_service_mock.session_repo.get_by_jti.return_value = old_session
    auth_service_mock.token_repo.verify_refresh_token.return_value = {"sub": "1"}

    # Mock security.create_access_refresh_tokens to return valid tokens
    with patch("robbot.services.auth_services.security") as mock_security:
        mock_security.create_access_refresh_tokens.return_value = {
            "access_token": "new_access",
            "refresh_token": "new_refresh",
        }

        # Attempt refresh should raise AuthException due to idle timeout
        with pytest.raises(AuthException) as exc_info:
            auth_service_mock.refresh("old_refresh_token", ip_address="192.168.1.1")

        assert "Session expired due to inactivity" in str(exc_info.value)
        # Verify session was marked as revoked
        auth_service_mock.session_repo.revoke.assert_called_once_with(1)


def test_idle_timeout_allows_recent_session(auth_service_mock):
    """Test that sessions active within 30 days are allowed."""
    # Create a session that was last used 15 days ago
    recent_session = MagicMock()
    recent_session.id = 2
    recent_session.user_id = 1
    recent_session.last_used_at = datetime.now(UTC) - timedelta(days=15)
    recent_session.created_at = datetime.now(UTC) - timedelta(days=20)
    recent_session.is_revoked = False
    recent_session.is_expired = False

    auth_service_mock.session_repo.get_by_jti.return_value = recent_session
    auth_service_mock.token_repo.verify_refresh_token.return_value = {"sub": "1"}

    # Mock security functions
    with patch("robbot.services.auth_services.security") as mock_security:
        mock_security.create_access_refresh_tokens.return_value = {
            "access_token": "new_access",
            "refresh_token": "new_refresh",
        }
        mock_security.parse_device_name.return_value = "Chrome on Windows"

        # Refresh should succeed
        result = auth_service_mock.refresh("valid_refresh_token", ip_address="192.168.1.1")

        # Verify session was updated (not revoked)
        assert isinstance(result, Token)
        auth_service_mock.session_repo.revoke.assert_not_called()
        auth_service_mock.session_repo.update_last_used.assert_called_once()


def test_idle_timeout_uses_created_at_if_no_last_used(auth_service_mock):
    """Test that created_at is used if last_used_at is None."""
    # Create a session with no last_used_at (edge case)
    session_no_last_used = MagicMock()
    session_no_last_used.id = 3
    session_no_last_used.last_used_at = None
    session_no_last_used.created_at = datetime.now(UTC) - timedelta(days=35)
    session_no_last_used.is_revoked = False
    session_no_last_used.is_expired = False

    auth_service_mock.session_repo.get_by_jti.return_value = session_no_last_used
    auth_service_mock.token_repo.verify_refresh_token.return_value = {"sub": "1"}

    with patch("robbot.services.auth_services.security"):
        # Should be revoked based on created_at
        with pytest.raises(AuthException) as exc_info:
            auth_service_mock.refresh("old_refresh_token", ip_address="192.168.1.1")

        assert "Session expired due to inactivity" in str(exc_info.value)
        auth_service_mock.session_repo.revoke.assert_called_once_with(3)


def test_idle_timeout_boundary_exactly_30_days(auth_service_mock):
    """Test that session at exactly 30 days is still valid."""
    # Create a session last used exactly 30 days ago
    boundary_session = MagicMock()
    boundary_session.id = 4
    boundary_session.user_id = 1
    boundary_session.last_used_at = datetime.now(UTC) - timedelta(days=30)
    boundary_session.created_at = datetime.now(UTC) - timedelta(days=40)
    boundary_session.is_revoked = False
    boundary_session.is_expired = False

    auth_service_mock.session_repo.get_by_jti.return_value = boundary_session
    auth_service_mock.token_repo.verify_refresh_token.return_value = {"sub": "1"}

    with patch("robbot.services.auth_services.security") as mock_security:
        mock_security.create_access_refresh_tokens.return_value = {
            "access_token": "new_access",
            "refresh_token": "new_refresh",
        }
        mock_security.parse_device_name.return_value = None

        # Should still be valid at exactly 30 days
        result = auth_service_mock.refresh("valid_refresh_token", ip_address="192.168.1.1")
        assert isinstance(result, Token)


def test_idle_timeout_message_clear(auth_service_mock):
    """Test that idle timeout error message is clear and actionable."""
    old_session = MagicMock()
    old_session.id = 5
    old_session.last_used_at = datetime.now(UTC) - timedelta(days=40)
    old_session.created_at = datetime.now(UTC) - timedelta(days=50)
    old_session.is_revoked = False
    old_session.is_expired = False

    auth_service_mock.session_repo.get_by_jti.return_value = old_session
    auth_service_mock.token_repo.verify_refresh_token.return_value = {"sub": "1"}

    with patch("robbot.services.auth_services.security"):
        with pytest.raises(AuthException) as exc_info:
            auth_service_mock.refresh("old_refresh_token", ip_address="192.168.1.1")

        error_msg = str(exc_info.value)
        # Verify message contains actionable information
        assert "30 days" in error_msg
        assert "Please login again" in error_msg
