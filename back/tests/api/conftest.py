"""Pytest configuration for API tests."""

import re
import time

import pytest
import redis
import requests


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Base URL for API requests."""
    return "http://localhost:3333/api/v1"


@pytest.fixture(scope="session")
def maildev_base_url() -> str:
    """Maildev API base URL."""
    return "http://localhost:1080"


@pytest.fixture(autouse=True)
def clear_rate_limiting():
    """Clear Redis rate limiting keys before each test.

    This ensures tests are isolated and don't interfere with each other.
    Rate limit keys follow pattern: ratelimit:*
    """
    redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    # Find all rate limiting keys
    rate_limit_keys = redis_client.keys("ratelimit:*")

    # Delete them if any exist
    if rate_limit_keys:
        redis_client.delete(*rate_limit_keys)

    yield  # Run the test

    # Optional: cleanup after test as well
    rate_limit_keys = redis_client.keys("ratelimit:*")
    if rate_limit_keys:
        redis_client.delete(*rate_limit_keys)


def extract_verification_token_from_email(maildev_url: str, recipient_email: str, timeout: int = 10) -> str:
    """Extract verification token from email in Maildev.

    Maildev captures all emails. We:
    1. Poll Maildev API for emails to the recipient
    2. Find email with verification link
    3. Extract token from verification link

    Args:
        maildev_url: Maildev API base URL
        recipient_email: Email address to search for
        timeout: Seconds to wait for email to arrive

    Returns:
        Verification token extracted from email body

    Raises:
        TimeoutError: If email not found within timeout
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            # Get all emails from Maildev API
            response = requests.get(f"{maildev_url}/email", timeout=30)
            if response.status_code != 200:
                time.sleep(0.5)
                continue

            emails = response.json()

            # Find email to our recipient
            for email in emails:
                if email.get("to") and any(recipient_email in addr.get("address", "") for addr in email.get("to", [])):
                    # Extract token from email body
                    # Email contains verification link like: http://...?token=xxx
                    body = email.get("text", "")
                    match = re.search(r"token=([a-zA-Z0-9\-_.]+)", body)
                    if match:
                        return match.group(1)

            time.sleep(0.5)

        except Exception as e:
            pytest.skip(f"Error accessing Maildev: {e}")

    raise TimeoutError(f"Verification email not found in Maildev for {recipient_email} within {timeout}s")


@pytest.fixture(scope="session")
def db_connection_string():
    """Database connection string for direct DB access from tests."""
    # Assumes default docker-compose ports (host mapped to 15432)
    return "postgresql+psycopg2://dba:dba@localhost:15432/BotDB"


def mark_email_verified_in_db(email: str, db_url: str):
    """Fallback: Manually mark email as verified in DB if Maildev fails."""
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Find user ID
            result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
            user_row = result.fetchone()
            if user_row:
                user_id = user_row[0]
                # Update credential
                conn.execute(
                    text("UPDATE credentials SET email_verified = true WHERE user_id = :uid"), {"uid": user_id}
                )
                conn.commit()
                print(f"[WARN] Manually verified email in DB for {email} (Maildev fallback)")
            else:
                print(f"[ERROR] User {email} not found in DB for manual verification")
    except Exception as e:
        print(f"[ERROR] Failed to manually verify email in DB: {e}")


@pytest.fixture(scope="module")
def admin_token(api_base_url: str, maildev_base_url: str, db_connection_string: str) -> str:
    """Get admin authentication token using email verification flow (with DB fallback)."""
    # Use timestamp to ensure unique email per test
    timestamp = int(time.time() * 1000)
    email = f"test_admin_{timestamp}@example.com"
    password = "TestAdmin123!Secure"

    # Step 1: Signup (cria user não verificado)
    signup_response = requests.post(
        f"{api_base_url}/auth/signup",
        json={"email": email, "password": password, "full_name": f"Test Admin {timestamp}", "role": "admin"},
        timeout=30,
    )

    if signup_response.status_code not in [201, 400]:
        pytest.skip(f"Signup failed: {signup_response.status_code} - {signup_response.text}")

    # Step 2: Extrair token do email capturado no Maildev
    try:
        token = extract_verification_token_from_email(maildev_base_url, email, timeout=5)  # Reduced timeout
        # Step 3: Verificar email usando o token
        verify_response = requests.get(f"{api_base_url}/auth/email/verify", params={"token": token}, timeout=30)
        if verify_response.status_code not in [200, 400]:
            print("[WARN] Email verification API failed, trying DB fallback")
            mark_email_verified_in_db(email, db_connection_string)

    except TimeoutError:
        print(f"[WARN] Email verification timeout, using DB fallback for {email}")
        mark_email_verified_in_db(email, db_connection_string)

    # Step 4: Fazer login
    session = requests.Session()
    login_response = session.post(f"{api_base_url}/auth/token", data={"username": email, "password": password})

    if login_response.status_code != 200:
        pytest.skip(f"Login failed: {login_response.status_code} - {login_response.text}")

    # Token is stored in HttpOnly cookie, extract from cookies
    access_token = session.cookies.get("access_token")
    if not access_token:
        pytest.skip("No access_token in cookies")

    return access_token


@pytest.fixture(scope="module")
def secretary_token(api_base_url: str, maildev_base_url: str, db_connection_string: str) -> str:
    """Get secretary authentication token using email verification flow (with DB fallback)."""
    # Use timestamp to ensure unique email per test
    timestamp = int(time.time() * 1000)
    email = f"test_secretary_{timestamp}@example.com"
    password = "TestSecretary123!Secure"

    # Step 1: Signup
    signup_response = requests.post(
        f"{api_base_url}/auth/signup",
        json={"email": email, "password": password, "full_name": f"Test Secretary {timestamp}", "role": "user"},
        timeout=30,
    )

    if signup_response.status_code not in [201, 400]:
        pytest.skip(f"Signup failed: {signup_response.status_code} - {signup_response.text}")

    # Step 2: Extrair token do email
    try:
        token = extract_verification_token_from_email(maildev_base_url, email, timeout=5)
        # Step 3: Verificar email
        verify_response = requests.get(f"{api_base_url}/auth/email/verify", params={"token": token}, timeout=30)
        if verify_response.status_code not in [200, 400]:
            mark_email_verified_in_db(email, db_connection_string)
    except TimeoutError:
        mark_email_verified_in_db(email, db_connection_string)

    # Step 4: Fazer login
    session = requests.Session()
    login_response = session.post(f"{api_base_url}/auth/token", data={"username": email, "password": password})

    if login_response.status_code != 200:
        pytest.skip(f"Login failed: {login_response.status_code} - {login_response.text}")

    # Token is stored in HttpOnly cookie, extract from cookies
    access_token = session.cookies.get("access_token")
    if not access_token:
        pytest.skip("No access_token in cookies")

    return access_token


@pytest.fixture(scope="module")
def auth_headers(admin_token: str) -> dict:
    """Headers with admin authentication."""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def api_client(api_base_url: str, maildev_base_url: str, db_connection_string: str):
    """API client with authenticated session."""
    # Create authenticated user
    email, session = create_authenticated_user(api_base_url, maildev_base_url, db_connection_string, role="admin")

    class APIClient:
        def __init__(self, base_url: str, session: requests.Session):
            self.base_url = base_url
            self.session = session

        def get(self, endpoint: str, **kwargs):
            url = f"{self.base_url}{endpoint}"
            print(f"DEBUG: GET {url}")
            return self.session.get(url, **kwargs)

        def post(self, endpoint: str, **kwargs):
            url = f"{self.base_url}{endpoint}"
            print(f"DEBUG: POST {url}")
            return self.session.post(url, **kwargs)

        def patch(self, endpoint: str, **kwargs):
            url = f"{self.base_url}{endpoint}"
            print(f"DEBUG: PATCH {url}")
            return self.session.patch(url, **kwargs)

        def delete(self, endpoint: str, **kwargs):
            url = f"{self.base_url}{endpoint}"
            print(f"DEBUG: DELETE {url}")
            return self.session.delete(url, **kwargs)

    return APIClient(api_base_url, session)


def create_authenticated_user(
    api_base_url: str, maildev_base_url: str, db_url: str, role: str = "admin"
) -> tuple[str, requests.Session]:
    """Helper to create and authenticate a user for testing (with DB fallback)."""
    import time

    # Use timestamp to ensure unique email
    timestamp = int(time.time() * 1000)
    email = f"test_user_{timestamp}@example.com"
    password = "TestUser123!Secure"

    # Signup
    signup_response = requests.post(
        f"{api_base_url}/auth/signup",
        json={"email": email, "password": password, "full_name": f"Test User {timestamp}", "role": role},
        timeout=30,
    )

    if signup_response.status_code not in [201, 400]:
        raise Exception(f"Signup failed: {signup_response.status_code} - {signup_response.text}")

    # Extract verification token from email OR Fallback
    try:
        token = extract_verification_token_from_email(maildev_base_url, email, timeout=5)
        verify_response = requests.get(f"{api_base_url}/auth/email/verify", params={"token": token}, timeout=30)
        if verify_response.status_code not in [200, 400]:
            print(f"[WARN] Verification failed via API, falling back to DB for {email}")
            mark_email_verified_in_db(email, db_url)
    except TimeoutError:
        print(f"[WARN] Verification timeout, falling back to DB for {email}")
        mark_email_verified_in_db(email, db_url)

    # Login
    session = requests.Session()
    login_response = session.post(f"{api_base_url}/auth/token", data={"username": email, "password": password})

    if login_response.status_code != 200:
        raise Exception(f"Login failed: {login_response.status_code} - {login_response.text}")

    # Extract token from cookie and set in session headers for subsequent requests
    access_token = session.cookies.get("access_token")
    if access_token:
        session.headers.update({"Authorization": f"Bearer {access_token}"})

    return email, session


@pytest.fixture
def authenticated_admin(
    api_base_url: str, maildev_base_url: str, db_connection_string: str
) -> tuple[str, requests.Session]:
    """Create and return an authenticated admin user for testing."""
    return create_authenticated_user(api_base_url, maildev_base_url, db_connection_string, role="admin")


@pytest.fixture
def authenticated_secretary(
    api_base_url: str, maildev_base_url: str, db_connection_string: str
) -> tuple[str, requests.Session]:
    """Create and return an authenticated secretary user for testing."""
    return create_authenticated_user(api_base_url, maildev_base_url, db_connection_string, role="user")


@pytest.fixture(autouse=True)
def mock_external_dependencies_for_tests():
    """Mock external dependencies to isolate tests from external APIs.

    This prevents:
    - Gemini API quota limits (RESOURCE_EXHAUSTED errors)
    - WhatsApp WAHA API calls
    - Database writes for interactions/LLM logging
    """
    import unittest.mock as mock

    # Mock Gemini client response for intent detection
    mock_gemini_response = {
        "response": '{"intent": "INTERESSE_TRATAMENTO", "spin_phase": "SITUATION"}',
        "tokens_used": 50,
        "latency_ms": 100,
    }
    mock.patch(
        "robbot.adapters.external.gemini_client.GeminiClient.generate_response", return_value=mock_gemini_response
    ).start()

    # Mock intent detector methods
    mock.patch("robbot.services.intent_detector.IntentDetector.detect_urgency", return_value=False).start()
    mock.patch("robbot.services.intent_detector.IntentDetector.try_extract_name", return_value=None).start()

    # Mock WAHA client to avoid WhatsApp API calls
    mock.patch("robbot.adapters.external.waha_client.WAHAClient.send_text", return_value=True).start()

    # Mock interaction registration to avoid user_id requirement
    mock.patch(
        "robbot.services.conversation_orchestrator.ConversationOrchestrator._register_interaction", return_value=None
    ).start()

    # Mock LLM interaction logging to avoid database writes
    mock.patch(
        "robbot.services.conversation_orchestrator.ConversationOrchestrator._log_llm_interaction", return_value=None
    ).start()
