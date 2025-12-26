"""Unit tests for email verification functionality.

FASE 4: Tests for email verification workflow:
- User signup creates unverified account
- Login blocked until email verified
- Email verification with token
- Resend verification email
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from robbot.services.email_verification_service import EmailVerificationService
from robbot.config.settings import settings
from robbot.services.auth_services import AuthService
from robbot.adapters.repositories.credential_repository import CredentialRepository
from robbot.adapters.repositories.user_repository import UserRepository
from robbot.core.exceptions import AuthException
from robbot.schemas.auth import SignupRequest


@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    
    # Create tables manually
    with engine.connect() as conn:
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
        
        conn.execute(text("""
            CREATE TABLE credentials (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                password_changed_at TIMESTAMP,
                email_verified BOOLEAN DEFAULT 0 NOT NULL,
                email_verification_token VARCHAR(255),
                email_verification_sent_at TIMESTAMP,
                reset_token VARCHAR(255),
                reset_token_expires_at TIMESTAMP,
                reset_token_used BOOLEAN DEFAULT 0,
                mfa_enabled BOOLEAN DEFAULT 0 NOT NULL,
                mfa_secret VARCHAR(255),
                backup_codes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        
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
        
        conn.execute(text("""
            CREATE TABLE revoked_tokens (
                id INTEGER PRIMARY KEY,
                token VARCHAR(512) UNIQUE NOT NULL,
                revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE audit_logs (
                id INTEGER PRIMARY KEY,
                action VARCHAR(100) NOT NULL,
                entity_type VARCHAR(50),
                entity_id VARCHAR(50),
                user_id INTEGER,
                old_value TEXT,
                new_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        """))
        
        conn.commit()
    
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_signup_creates_unverified_user(db_session):
    """Test that signup creates user with email_verified=false."""
    auth_service = AuthService(db_session)
    credential_repo = CredentialRepository(db_session)
    
    signup_data = SignupRequest(
        email="test@example.com",
        password="SecurePass123!",
        full_name="Test User"
    )
    
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
    signup_data = SignupRequest(
        email="test@example.com",
        password="SecurePass123!",
        full_name="Test User"
    )
    auth_service.signup(signup_data)
    
    # Try to login (should fail - email not verified)
    with pytest.raises(AuthException, match="Email not verified"):
        auth_service.authenticate_user(
            "test@example.com",
            "SecurePass123!",
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1"
        )


def test_verify_email_success(db_session):
    """Test successful email verification."""
    auth_service = AuthService(db_session)
    email_verification_service = EmailVerificationService(db_session)
    credential_repo = CredentialRepository(db_session)
    
    # Create user
    signup_data = SignupRequest(
        email="test@example.com",
        password="SecurePass123!",
        full_name="Test User"
    )
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
    signup_data = SignupRequest(
        email="test@example.com",
        password="SecurePass123!",
        full_name="Test User"
    )
    user = auth_service.signup(signup_data)
    
    # Verify email
    credential = credential_repo.get_by_user_id(user.id)
    email_verification_service.verify_email(credential.email_verification_token)
    
    # Login should work now
    token_result = auth_service.authenticate_user(
        "test@example.com",
        "SecurePass123!",
        user_agent="Mozilla/5.0",
        ip_address="127.0.0.1"
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
    signup_data = SignupRequest(
        email="test@example.com",
        password="SecurePass123!",
        full_name="Test User"
    )
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
    signup_data = SignupRequest(
        email="test@example.com",
        password="SecurePass123!",
        full_name="Test User"
    )
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
    signup_data = SignupRequest(
        email="test@example.com",
        password="SecurePass123!",
        full_name="Test User"
    )
    user = auth_service.signup(signup_data)
    credential = credential_repo.get_by_user_id(user.id)
    email_verification_service.verify_email(credential.email_verification_token)
    
    # Try to resend
    with pytest.raises(AuthException, match="Email already verified"):
        email_verification_service.resend_verification_email("test@example.com")
