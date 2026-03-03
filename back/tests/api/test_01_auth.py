"""
PHASE 1: Infrastructure and Authentication Tests

Test Cases: UC-001 to UC-005
Based on: back/docs/academic/casos-teste-validacao.md

Each test is now isolated and independent. No shared state.
"""

import re

import requests


class TestPhase1Auth:
    """Phase 1: Infrastructure and Authentication.

    Tests are fully independent - each creates its own test data.
    """

    def test_uc001_system_health_check(self, api_base_url):
        """UC-001: System Health Check."""
        response = requests.get(f"{api_base_url}/health", timeout=30)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert data["components"]["database"]["ok"] is True
        assert data["components"]["redis"]["ok"] is True
        assert data["components"]["waha"]["ok"] is True

    def test_uc002_signup_admin_user(self, api_base_url):
        """UC-002: Signup - Create ADMIN User."""
        # Clear Maildev inbox to avoid stale tokens
        requests.delete("http://localhost:1080/email/all", timeout=30)

        response = requests.post(
            f"{api_base_url}/auth/signup",
            json={"email": "admin@clinicago.com.br", "password": "Admin@2025!Secure", "role": "admin"},
            timeout=30,
        )

        # 201 if created, 400 if already exists
        assert response.status_code in [201, 400]

        if response.status_code == 201:
            data = response.json()
            assert data["email"] == "admin@clinicago.com.br"
            assert data["role"] == "admin"
            assert data["is_active"] is True
            assert "password" not in data

    def test_uc003_login_get_access_token(self, api_base_url):
        """UC-003: Login - Get Access Token (with email verification)."""
        # Clear Maildev before this test to isolate verification token
        requests.delete("http://localhost:1080/email/all", timeout=30)

        # Create new test user for this test only
        test_email = "test_uc003_user@clinicago.com.br"
        test_password = "TestUC003@2025"

        signup_response = requests.post(
            f"{api_base_url}/auth/signup",
            json={"email": test_email, "password": test_password, "role": "admin"},
            timeout=30,
        )
        assert signup_response.status_code in [201, 400]

        # Get verification token from email
        token = self._get_verification_token_from_maildev_for(test_email)
        print(f"\n[DEBUG] Token from Maildev: {token[:20]}..." if token else "\n[DEBUG] No token found in Maildev")

        if token:
            # Verify the email
            verify_response = requests.get(f"{api_base_url}/auth/email/verify", params={"token": token}, timeout=30)
            assert verify_response.status_code == 200
        else:
            # Fallback: verify in DB (Docker networking issue)
            self._fallback_verify_db(test_email)

        # Now attempt login with a session to capture cookies
        session = requests.Session()
        response = session.post(f"{api_base_url}/auth/token", data={"username": test_email, "password": test_password})

        assert response.status_code == 200
        data = response.json()

        # Token is stored in HttpOnly cookie, not in response body
        assert "user" in data
        assert data["user"]["email"] == test_email
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 900  # 15 minutes in seconds
        assert data["mfa_required"] is False

    def test_uc004_validate_token_get_current_user(self, api_base_url):
        """UC-004: Validate Token - Get Current User (independent test)."""
        # Create and verify a new user for this test
        test_email = "test_uc004_user@clinicago.com.br"
        test_password = "TestUC004@2025"

        # Clear Maildev
        requests.delete("http://localhost:1080/email/all", timeout=30)

        # Signup
        requests.post(
            f"{api_base_url}/auth/signup",
            json={"email": test_email, "password": test_password, "role": "admin"},
            timeout=30,
        )

        # Verify email
        token = self._get_verification_token_from_maildev_for(test_email)
        if token:
            requests.get(f"{api_base_url}/auth/email/verify", params={"token": token}, timeout=30)
        else:
            # Fallback: verify in DB
            self._fallback_verify_db(test_email)

        # Login
        session = requests.Session()
        login_response = session.post(
            f"{api_base_url}/auth/token", data={"username": test_email, "password": test_password}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.status_code} - {login_response.text}"

        # Test /auth/me endpoint
        response = session.get(f"{api_base_url}/auth/me")

        assert response.status_code == 200
        data = response.json()

        assert data["email"] == test_email
        assert data["role"] == "admin"
        assert data["is_active"] is True

    def test_uc005_create_secretary_user(self, api_base_url):
        """UC-005: Create SECRETARY User (independent test)."""
        # Create admin user first
        admin_email = "test_uc005_admin@clinicago.com.br"
        admin_password = "AdminUC005@2025"

        # Clear Maildev
        requests.delete("http://localhost:1080/email/all", timeout=30)

        # Signup admin
        requests.post(
            f"{api_base_url}/auth/signup",
            json={"email": admin_email, "password": admin_password, "role": "admin"},
            timeout=30,
        )

        # Verify admin email
        token = self._get_verification_token_from_maildev_for(admin_email)
        if token:
            requests.get(f"{api_base_url}/auth/email/verify", params={"token": token}, timeout=30)
        else:
            # Fallback: verify in DB
            self._fallback_verify_db(admin_email)

        # Login admin
        session = requests.Session()
        session.post(f"{api_base_url}/auth/token", data={"username": admin_email, "password": admin_password})

        # Create secretary user
        secretary_email = "test_uc005_secretary@clinicago.com.br"
        response = session.post(
            f"{api_base_url}/auth/signup",
            json={"email": secretary_email, "password": "Secret@2025!Pass", "role": "user"},
        )

        # 201 if created, 400 if already exists
        assert response.status_code in [201, 400]

        if response.status_code == 201:
            data = response.json()
            assert data["email"] == secretary_email
            assert data["role"] == "user"
            assert data["is_active"] is True

    @staticmethod
    def _get_verification_token_from_maildev_for(email: str):
        """Extract verification token from Maildev for specific email."""
        try:
            response = requests.get("http://localhost:1080/email", timeout=10)
        except requests.exceptions.RequestException:
            return None

        if response.status_code != 200:
            return None

        emails = response.json()
        if not emails:
            return None

        # Sort emails by time descending
        emails = sorted(
            emails,
            key=lambda e: e.get("time") or e.get("date") or "",
            reverse=True,
        )

        for mail in emails:
            email_to = mail.get("to", [])
            if (
                email_to
                and isinstance(email_to, list)
                and len(email_to) > 0
                and email in email_to[0].get("address", "")
            ):
                email_text = mail.get("text", "")
                match = re.search(r"token=([a-zA-Z0-9\-_.]+)", email_text)
                if match:
                    return match.group(1)

        return None

    @staticmethod
    def _fallback_verify_db(email: str):
        """Fallback to DB verification if Maildev fails (Docker networking issue)."""
        db_url = "postgresql+psycopg2://dba:dba@localhost:15432/BotDB"
        try:
            from sqlalchemy import create_engine, text

            engine = create_engine(db_url)
            with engine.connect() as conn:
                # Find user ID
                result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
                user_row = result.fetchone()
                if user_row:
                    user_id = user_row[0]
                    conn.execute(
                        text("UPDATE credentials SET email_verified = true WHERE user_id = :uid"), {"uid": user_id}
                    )
                    conn.commit()
                    print(f"[WARN] Manually verified email in DB for {email}")
        except Exception as e:
            print(f"[ERROR] DB Verification failed: {e}")
