"""Unit tests for MFA endpoints (FASE 5)."""

import pytest
from unittest.mock import Mock, patch

from robbot.main import app
from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.core.exceptions import AuthException


@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock()


@pytest.fixture
def mock_current_user():
    """Mock authenticated user."""
    user = Mock()
    user.id = 1
    user.email = "test@example.com"
    return user


@pytest.fixture
def client_with_auth(mock_current_user, mock_db):
    """Test client with mocked authentication."""
    from fastapi.testclient import TestClient
    
    # Override dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    app.dependency_overrides[get_db] = lambda: mock_db
    
    client = TestClient(app)
    yield client
    
    # Clear overrides after test
    app.dependency_overrides.clear()


class TestMfaSetup:
    """Tests for POST /auth/mfa/setup endpoint."""
    
    def test_setup_mfa_success(self, client_with_auth):
        """Test successful MFA setup."""
        with patch("robbot.services.mfa_service.MfaService.setup_mfa") as mock_setup:
            mock_setup.return_value = (
                "JBSWY3DPEHPK3PXP",
                "base64_qr_code_string",
                ["code1", "code2", "code3", "code4", "code5", "code6", "code7", "code8", "code9", "code10"]
            )
            
            response = client_with_auth.post("/api/v1/auth/mfa/setup")
            
            assert response.status_code == 200
            data = response.json()
            assert data["secret"] == "JBSWY3DPEHPK3PXP"
            assert data["qr_code_base64"] == "base64_qr_code_string"
            assert len(data["backup_codes"]) == 10
            mock_setup.assert_called_once_with(1)
    
    def test_setup_mfa_already_enabled(self, client_with_auth):
        """Test MFA setup when already enabled."""
        with patch("robbot.services.mfa_service.MfaService.setup_mfa") as mock_setup:
            mock_setup.side_effect = AuthException("MFA already enabled")
            
            response = client_with_auth.post("/api/v1/auth/mfa/setup")
            
            assert response.status_code == 400
            assert "MFA already enabled" in response.json()["detail"]
    
    def test_setup_mfa_unauthenticated(self):
        """Test MFA setup without authentication."""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.post("/api/v1/auth/mfa/setup")
        assert response.status_code == 401


class TestMfaVerify:
    """Tests for POST /auth/mfa/verify endpoint."""
    
    def test_verify_mfa_totp_success(self, client_with_auth):
        """Test successful TOTP verification."""
        with patch("robbot.services.mfa_service.MfaService.verify_mfa") as mock_verify:
            mock_verify.return_value = True
            
            response = client_with_auth.post("/api/v1/auth/mfa/verify", json={"code": "123456"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["verified"] is True
            assert "successfully" in data["message"]
            mock_verify.assert_called_once_with(1, "123456")
    
    def test_verify_mfa_backup_code_success(self, client_with_auth):
        """Test successful backup code verification."""
        with patch("robbot.services.mfa_service.MfaService.verify_mfa") as mock_verify_totp:
            with patch("robbot.services.mfa_service.MfaService.verify_backup_code") as mock_verify_backup:
                # TOTP fails
                mock_verify_totp.side_effect = AuthException("Invalid MFA code")
                # Backup succeeds
                mock_verify_backup.return_value = True
                
                response = client_with_auth.post("/api/v1/auth/mfa/verify", json={"code": "abc123"})
                
                assert response.status_code == 200
                data = response.json()
                assert data["verified"] is True
                assert "Backup code" in data["message"]
    
    def test_verify_mfa_invalid_code(self, client_with_auth):
        """Test verification with invalid code."""
        with patch("robbot.services.mfa_service.MfaService.verify_mfa") as mock_verify_totp:
            with patch("robbot.services.mfa_service.MfaService.verify_backup_code") as mock_verify_backup:
                mock_verify_totp.side_effect = AuthException("Invalid MFA code")
                mock_verify_backup.side_effect = AuthException("Invalid backup code")
                
                response = client_with_auth.post("/api/v1/auth/mfa/verify", json={"code": "000000"})
                
                assert response.status_code == 401
    
    def test_verify_mfa_not_enabled(self, client_with_auth):
        """Test verification when MFA not enabled."""
        with patch("robbot.services.mfa_service.MfaService.verify_mfa") as mock_verify:
            with patch("robbot.services.mfa_service.MfaService.verify_backup_code") as mock_backup:
                mock_verify.side_effect = AuthException("MFA not enabled")
                mock_backup.side_effect = AuthException("MFA not enabled")
                
                response = client_with_auth.post("/api/v1/auth/mfa/verify", json={"code": "123456"})
                
                assert response.status_code == 401


class TestMfaDisable:
    """Tests for POST /auth/mfa/disable endpoint."""
    
    def test_disable_mfa_success(self, client_with_auth):
        """Test successful MFA disabling."""
        with patch("robbot.services.mfa_service.MfaService.verify_mfa") as mock_verify:
            with patch("robbot.services.mfa_service.MfaService.disable_mfa") as mock_disable:
                mock_verify.return_value = True
                
                response = client_with_auth.post("/api/v1/auth/mfa/disable", json={"code": "123456"})
                
                assert response.status_code == 200
                data = response.json()
                assert "disabled successfully" in data["message"]
                mock_verify.assert_called_once_with(1, "123456")
                mock_disable.assert_called_once_with(1)
    
    def test_disable_mfa_invalid_code(self, client_with_auth):
        """Test MFA disabling with invalid code."""
        with patch("robbot.services.mfa_service.MfaService.verify_mfa") as mock_verify:
            mock_verify.side_effect = AuthException("Invalid MFA code")
            
            response = client_with_auth.post("/api/v1/auth/mfa/disable", json={"code": "000000"})
            
            assert response.status_code == 401
    
    def test_disable_mfa_not_enabled(self, client_with_auth):
        """Test MFA disabling when not enabled."""
        with patch("robbot.services.mfa_service.MfaService.verify_mfa") as mock_verify:
            mock_verify.side_effect = AuthException("MFA not enabled")
            
            response = client_with_auth.post("/api/v1/auth/mfa/disable", json={"code": "123456"})
            
            assert response.status_code == 401
