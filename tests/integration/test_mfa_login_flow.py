"""Integration tests for complete MFA login flow.

Tests the full authentication flow with MFA enabled:
1. User logs in with email/password
2. If MFA enabled, receives temporary token
3. User provides TOTP code
4. Receives final access/refresh tokens
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from types import SimpleNamespace

from robbot.main import app as application
from robbot.api.v1.dependencies import get_current_user, get_db


@pytest.fixture
def client():
    """Create test client with rate limiter disabled (stubbed)."""
    # Stub rate limiter to always allow requests in tests
    limiter_stub = SimpleNamespace(check_rate_limit=lambda **kwargs: (True, 0, 0))
    rate_patch = patch("robbot.core.rate_limiting.get_rate_limiter", return_value=limiter_stub)
    rate_patch.start()
    try:
        yield TestClient(application)
    finally:
        rate_patch.stop()


@pytest.fixture
def client_with_mfa_user(client: TestClient):
    """Create a test user with MFA enabled.
    
    Returns client with user configured for MFA testing.
    """
    # Mock database session
    mock_db = MagicMock(spec=Session)
    
    # Mock user with MFA enabled
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.email = "mfa@example.com"
    mock_user.is_active = True
    mock_user.full_name = "MFA User"
    
    # Override dependencies
    application.dependency_overrides[get_db] = lambda: mock_db
    
    yield client, mock_db, mock_user
    
    # Cleanup
    application.dependency_overrides.clear()


class TestMfaLoginFlow:
    """Test complete MFA login flow."""
    
    @patch("robbot.services.auth_services.AuthService.authenticate_user")
    def test_login_with_mfa_enabled_returns_temporary_token(
        self,
        mock_authenticate,
        client_with_mfa_user,
    ):
        """Test that login with MFA enabled returns temporary token."""
        client, mock_db, mock_user = client_with_mfa_user
        
        # Mock authentication to return object with mfa_required=True
        mock_token = SimpleNamespace(
            access_token="temporary_token_123",
            refresh_token="",
            mfa_required=True,
            user=mock_user,
        )
        mock_authenticate.return_value = mock_token
        
        # Login
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "mfa@example.com", "password": "Password123!"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["mfa_required"] is True
        assert "temporary_token" in data
        assert data["temporary_token"] == "temporary_token_123"
        assert "message" in data
        
    @patch("robbot.services.auth_services.AuthService.authenticate_user")
    def test_login_without_mfa_returns_final_tokens(
        self,
        mock_authenticate,
        client_with_mfa_user,
    ):
        """Test that login without MFA returns final tokens immediately."""
        client, mock_db, mock_user = client_with_mfa_user
        
        # Mock authentication to return object with mfa_required=False
        mock_token = SimpleNamespace(
            access_token="access_token_123",
            refresh_token="refresh_token_123",
            mfa_required=False,
            user=mock_user,
        )
        mock_authenticate.return_value = mock_token
        
        # Login
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "user@example.com", "password": "Password123!"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["mfa_required"] is False
        assert "user" in data
        
        # Check cookies
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
    
    @patch("robbot.services.auth_services.AuthService.verify_mfa_and_complete_login")
    def test_mfa_login_with_valid_code_returns_tokens(
        self,
        mock_verify_mfa,
        client_with_mfa_user,
    ):
        """Test MFA login with valid TOTP code returns final tokens."""
        client, mock_db, mock_user = client_with_mfa_user
        
        # Mock MFA verification success
        mock_token = SimpleNamespace(
            access_token="final_access_token",
            refresh_token="final_refresh_token",
            user=mock_user,
        )
        mock_verify_mfa.return_value = mock_token
        
        # Complete MFA login
        response = client.post(
            "/api/v1/auth/mfa/login",
            json={
                "temporary_token": "temporary_token_123",
                "code": "123456",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "final_access_token"
        assert data["refresh_token"] == "final_refresh_token"
        assert data["mfa_required"] is False
        assert data["temporary"] is False
        
        # Verify the service was called with correct params
        mock_verify_mfa.assert_called_once()
        call_args = mock_verify_mfa.call_args
        assert call_args.kwargs["temporary_token"] == "temporary_token_123"
        assert call_args.kwargs["code"] == "123456"
    
    @patch("robbot.services.auth_services.AuthService.verify_mfa_and_complete_login")
    def test_mfa_login_with_invalid_code_fails(
        self,
        mock_verify_mfa,
        client_with_mfa_user,
    ):
        """Test MFA login with invalid code returns 401."""
        client, mock_db, mock_user = client_with_mfa_user
        
        # Mock MFA verification failure
        from robbot.core.exceptions import AuthException
        mock_verify_mfa.side_effect = AuthException("Invalid MFA code")
        
        # Attempt MFA login with invalid code
        response = client.post(
            "/api/v1/auth/mfa/login",
            json={
                "temporary_token": "temporary_token_123",
                "code": "000000",
            },
        )
        
        assert response.status_code == 401
        assert "Invalid MFA code" in response.json()["detail"]
    
    @patch("robbot.services.auth_services.AuthService.verify_mfa_and_complete_login")
    def test_mfa_login_with_expired_temporary_token_fails(
        self,
        mock_verify_mfa,
        client_with_mfa_user,
    ):
        """Test MFA login with expired temporary token returns 401."""
        client, mock_db, mock_user = client_with_mfa_user
        
        # Mock expired token error
        from robbot.core.exceptions import AuthException
        mock_verify_mfa.side_effect = AuthException("Invalid or expired temporary token")
        
        # Attempt MFA login with expired token
        response = client.post(
            "/api/v1/auth/mfa/login",
            json={
                "temporary_token": "expired_token",
                "code": "123456",
            },
        )
        
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()
    
    @patch("robbot.services.auth_services.AuthService.verify_mfa_and_complete_login")
    def test_mfa_login_with_backup_code_success(
        self,
        mock_verify_mfa,
        client_with_mfa_user,
    ):
        """Test MFA login with valid backup code returns tokens."""
        client, mock_db, mock_user = client_with_mfa_user
        
        # Mock backup code verification success
        mock_token = SimpleNamespace(
            access_token="final_access_token",
            refresh_token="final_refresh_token",
            user=mock_user,
        )
        mock_verify_mfa.return_value = mock_token
        
        # Complete MFA login with backup code
        response = client.post(
            "/api/v1/auth/mfa/login",
            json={
                "temporary_token": "temporary_token_123",
                "code": "abc123",  # Backup code format
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "final_access_token"
        assert data["refresh_token"] == "final_refresh_token"


class TestMfaLoginValidation:
    """Test MFA login request validation."""
    
    def test_mfa_login_requires_temporary_token(self, client_with_mfa_user):
        """Test that MFA login requires temporary_token field."""
        client, _, _ = client_with_mfa_user
        
        response = client.post(
            "/api/v1/auth/mfa/login",
            json={"code": "123456"},  # Missing temporary_token
        )
        
        assert response.status_code == 422
    
    def test_mfa_login_requires_code(self, client_with_mfa_user):
        """Test that MFA login requires code field."""
        client, _, _ = client_with_mfa_user
        
        response = client.post(
            "/api/v1/auth/mfa/login",
            json={"temporary_token": "token123"},  # Missing code
        )
        
        assert response.status_code == 422
    
    def test_mfa_login_code_must_be_6_chars(self, client_with_mfa_user):
        """Test that MFA code must be exactly 6 characters."""
        client, _, _ = client_with_mfa_user
        
        # Too short
        response = client.post(
            "/api/v1/auth/mfa/login",
            json={"temporary_token": "token123", "code": "12345"},
        )
        assert response.status_code == 422
        
        # Too long
        response = client.post(
            "/api/v1/auth/mfa/login",
            json={"temporary_token": "token123", "code": "1234567"},
        )
        assert response.status_code == 422
