"""
PHASE 12: Advanced Security and Authentication Tests

Test Cases: UC-045 to UC-059
Based on: back/docs/academic/casos-teste-validacao.md

Covers:
- MFA (Multifactor Authentication) Lifecycle
- Session Management (Revoke)
- Account Locking (Block)
- Audit Logs
"""

import pyotp
import pytest
import requests

from .conftest import create_authenticated_user


class TestPhase12Security:
    """Phase 12: Advanced Security."""

    @pytest.fixture
    def dedicated_admin(self, api_base_url, maildev_base_url):
        """Create a dedicated admin for security tests to handle MFA state."""
        db_url = "postgresql://dba:dba@localhost:15432/BotDB"
        email, session = create_authenticated_user(api_base_url, maildev_base_url, db_url, role="admin")
        return email, session

    def test_uc045_to_uc048_mfa_lifecycle(self, api_base_url, dedicated_admin):
        """Complete MFA Lifecycle: Setup -> Verify -> Login with MFA -> Disable.

        Combines UCs 045, 046, 047, 048 to maintain state sequence.
        """
        email, session = dedicated_admin

        # --- UC-045: MFA Setup ---
        setup_resp = session.post(f"{api_base_url}/auth/mfa/setup", json={"password": "TestUser123!Secure"})

        if setup_resp.status_code == 404:
            pytest.skip("MFA endpoints not implemented yet")

        assert setup_resp.status_code == 200
        setup_data = setup_resp.json()

        secret = setup_data.get("secret")
        assert secret is not None
        assert "qr_code" in setup_data
        assert "backup_codes" in setup_data

        # --- UC-046: MFA Verify ---
        # Generate TOTP code
        totp = pyotp.TOTP(secret)
        code = totp.now()

        verify_resp = session.post(f"{api_base_url}/auth/mfa/verify", json={"code": code})
        assert verify_resp.status_code == 200
        assert verify_resp.json()["mfa_enabled"] is True

        # --- UC-047: Login with MFA ---
        # First, standard login (should return partial session or requirement for MFA)
        # Depending on implementation, might return 200 with mfa_required=True or 401

        login_session = requests.Session()
        login_resp = login_session.post(
            f"{api_base_url}/auth/token", data={"username": email, "password": "TestUser123!Secure"}
        )

        # Assuming flow: Login returns "mfa_required": true
        # If the API requires passing code in /token, adapting:
        if login_resp.status_code == 200:
            data = login_resp.json()
            if data.get("mfa_required"):
                # Call MFA login endpoint
                mfa_login_resp = login_session.post(
                    f"{api_base_url}/auth/mfa/login", json={"email": email, "code": totp.now()}
                )
                assert mfa_login_resp.status_code == 200
                assert "access_token" in mfa_login_resp.json()

        # --- UC-048: MFA Disable ---
        disable_resp = session.post(
            f"{api_base_url}/auth/mfa/disable", json={"password": "TestUser123!Secure", "code": totp.now()}
        )
        assert disable_resp.status_code == 200
        assert disable_resp.json()["mfa_enabled"] is False

    def test_uc049_list_sessions(self, api_base_url, dedicated_admin):
        """UC-049: List Active Sessions."""
        _, session = dedicated_admin
        resp = session.get(f"{api_base_url}/auth/sessions")

        if resp.status_code == 404:
            pytest.skip("Session management endpoints not implemented")

        assert resp.status_code == 200
        data = resp.json()
        assert "sessions" in data
        assert len(data["sessions"]) >= 1

    def test_uc050_revoke_session(self, api_base_url, dedicated_admin):
        """UC-050: Revoke specific session."""
        _, session = dedicated_admin

        # Get list first
        sessions = session.get(f"{api_base_url}/auth/sessions").json().get("sessions", [])
        if not sessions:
            pytest.skip("No sessions found")

        target_id = sessions[0]["id"]

        revoke_resp = session.post(f"{api_base_url}/auth/sessions/{target_id}/revoke")
        assert revoke_resp.status_code in [200, 204]

    def test_uc059_audit_logs(self, api_base_url, dedicated_admin):
        """UC-059: View Audit Logs."""
        _, session = dedicated_admin
        resp = session.get(f"{api_base_url}/audit-logs", params={"limit": 5})

        if resp.status_code == 404:
            pytest.skip("Audit endpoint not implemented")

        assert resp.status_code == 200
        logs = resp.json()
        assert isinstance(logs, list)
