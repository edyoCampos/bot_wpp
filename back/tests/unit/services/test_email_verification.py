"""Unit tests for email verification functionality.

FASE 4: Tests for email verification workflow:
- User signup creates unverified account
- Login blocked until email verified
- Email verification with token
- Resend verification email
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from robbot.infra.persistence.repositories.credential_repository import CredentialRepository
from robbot.config.settings import settings
from robbot.core.custom_exceptions import AuthException
from robbot.schemas.auth import SignupRequest
from robbot.services.auth.auth_services import AuthService
from robbot.services.auth.email_verification_service import EmailVerificationService

from robbot.infra.persistence.models.user_model import UserModel
from robbot.infra.persistence.models.credential_model import CredentialModel
from robbot.infra.persistence.models.auth_session_model import AuthSessionModel
from robbot.infra.persistence.models.revoked_token_model import RevokedTokenModel
from robbot.infra.persistence.models.audit_log_model import AuditLogModel


@pytest.fixture
def db_session_instance():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")

    # Create tables using SQLAlchemy Metadata
    UserModel.__table__.create(bind=engine)
    CredentialModel.__table__.create(bind=engine)
    AuthSessionModel.__table__.create(bind=engine)
    RevokedTokenModel.__table__.create(bind=engine)
    AuditLogModel.__table__.create(bind=engine)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()


def test_signup_creates_unverified_user(db_session):
    """Test that signup creates user with email_verified=false."""
    auth_service = AuthService(db_session)
    credential_repo = CredentialRepository(db_session)

    signup_data = SignupRequest(email="test@example.com", password="SecurePass123!", full_name="Test User")

    user = auth_service.signup(signup_data)

    # User should be created
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"

    # Credential should exist with email_verified=false
    credential = credential_repo.get_by_user_id(user.id)
    assert credential is not None
    assert credential.email_verified is False
    assert credential.email_verification_token is not None
    assert len(credential.email_verification_token) > 30  # Secure token


def test_login_blocked_for_unverified_email(db_session):
    """Test that login is blocked if email is not verified."""
    auth_service = AuthService(db_session)

    # Create user
    signup_data = SignupRequest(email="test@example.com", password="SecurePass123!", full_name="Test User")
    auth_service.signup(signup_data)

    # Try to login (should fail - email not verified)
    with pytest.raises(AuthException, match="Email not verified"):
        auth_service.authenticate_user(
            "test@example.com", "SecurePass123!", user_agent="Mozilla/5.0", ip_address="127.0.0.1"
        )


def test_verify_email_success(db_session):
    """Test successful email verification."""
    auth_service = AuthService(db_session)
    email_verification_service = EmailVerificationService(db_session)
    credential_repo = CredentialRepository(db_session)

    # Create user
    signup_data = SignupRequest(email="test@example.com", password="SecurePass123!", full_name="Test User")
    user = auth_service.signup(signup_data)

    # Get verification token
    credential = credential_repo.get_by_user_id(user.id)
    token = credential.email_verification_token

    # Verify email
    verified_user_id = email_verification_service.verify_email(token)

    # Check verification
    assert verified_user_id == user.id
    credential = credential_repo.get_by_user_id(user.id)
    assert credential.email_verified is True
    assert credential.email_verification_token is None  # Token cleared


def test_login_allowed_after_verification(db_session):
    """Test that login works after email verification."""
    auth_service = AuthService(db_session)
    email_verification_service = EmailVerificationService(db_session)
    credential_repo = CredentialRepository(db_session)

    # Create user
    signup_data = SignupRequest(email="test@example.com", password="SecurePass123!", full_name="Test User")
    user = auth_service.signup(signup_data)

    # Verify email
    credential = credential_repo.get_by_user_id(user.id)
    email_verification_service.verify_email(credential.email_verification_token)

    # Login should work now
    token_result = auth_service.authenticate_user(
        "test@example.com", "SecurePass123!", user_agent="Mozilla/5.0", ip_address="127.0.0.1"
    )

    assert token_result is not None
    assert token_result.access_token is not None
    assert token_result.refresh_token is not None


def test_verify_email_invalid_token(db_session):
    """Test email verification with invalid token."""
    email_verification_service = EmailVerificationService(db_session)

    with pytest.raises(AuthException, match="Invalid verification token"):
        email_verification_service.verify_email("invalid_token_12345")


def test_verify_email_already_verified(db_session):
    """Test that verifying already-verified email raises error."""
    auth_service = AuthService(db_session)
    email_verification_service = EmailVerificationService(db_session)
    credential_repo = CredentialRepository(db_session)

    # Create and verify user
    signup_data = SignupRequest(email="test@example.com", password="SecurePass123!", full_name="Test User")
    user = auth_service.signup(signup_data)
    credential = credential_repo.get_by_user_id(user.id)
    token = credential.email_verification_token
    email_verification_service.verify_email(token)

    # Try to verify again (token already invalidated)
    with pytest.raises(AuthException, match="Invalid verification token"):
        email_verification_service.verify_email(token)


def test_resend_verification_email(db_session):
    """Test resending verification email generates new token."""
    # Disable rate limiting for unit test
    settings.EMAIL_VERIFICATION_RESEND_MIN_INTERVAL_MINUTES = 0
    auth_service = AuthService(db_session)
    email_verification_service = EmailVerificationService(db_session)
    credential_repo = CredentialRepository(db_session)

    # Create user
    signup_data = SignupRequest(email="test@example.com", password="SecurePass123!", full_name="Test User")
    user = auth_service.signup(signup_data)

    # Get first token
    credential = credential_repo.get_by_user_id(user.id)
    first_token = credential.email_verification_token

    # Resend verification email
    new_token = email_verification_service.resend_verification_email("test@example.com")

    # Token should be different
    assert new_token != first_token
    credential = credential_repo.get_by_user_id(user.id)
    assert credential.email_verification_token == new_token


def test_resend_email_already_verified(db_session):
    """Test that resending email for verified account raises error."""
    auth_service = AuthService(db_session)
    email_verification_service = EmailVerificationService(db_session)
    credential_repo = CredentialRepository(db_session)

    # Create and verify user
    signup_data = SignupRequest(email="test@example.com", password="SecurePass123!", full_name="Test User")
    user = auth_service.signup(signup_data)
    credential = credential_repo.get_by_user_id(user.id)
    email_verification_service.verify_email(credential.email_verification_token)

    # Try to resend
    with pytest.raises(AuthException, match="Email already verified"):
        email_verification_service.resend_verification_email("test@example.com")
