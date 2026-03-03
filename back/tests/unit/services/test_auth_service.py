"""Unit tests for AuthService.

Tests user authentication, token management, MFA, and session handling.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from robbot.infra.persistence.repositories.credential_repository import CredentialRepository
from robbot.core import security
from robbot.core.custom_exceptions import AuthException
from robbot.infra.persistence.models.audit_log_model import AuditLogModel
from robbot.infra.persistence.models.auth_session_model import AuthSessionModel
from robbot.infra.persistence.models.credential_model import CredentialModel
from robbot.infra.persistence.models.revoked_token_model import RevokedTokenModel
from robbot.infra.persistence.models.user_model import UserModel
from robbot.schemas.user import UserCreate
from robbot.services.auth.auth_services import AuthService


@pytest.fixture(name="db_session")
def db_session_instance():
    # Use in-memory SQLite for fast unit testing
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    # Create only required tables to avoid enum/type issues
    UserModel.__table__.create(bind=engine)
    CredentialModel.__table__.create(bind=engine)
    RevokedTokenModel.__table__.create(bind=engine)
    AuthSessionModel.__table__.create(bind=engine)
    AuditLogModel.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = session_local()
    try:
        yield session
    finally:
        session.close()


def test_signup_creates_user_and_credential(db_session):
    svc = AuthService(db_session)
    payload = UserCreate(email="unit@example.com", password="StrongPass123!", full_name="Unit", role="user")

    user = svc.signup(payload)

    assert user.id is not None
    assert user.email == payload.email

    # Verify credential exists and has hashed password
    cred_repo = CredentialRepository(db_session)
    cred = cred_repo.get_by_user_id(user.id)
    assert cred is not None
    assert isinstance(cred.hashed_password, str) and len(cred.hashed_password) > 0


def test_authenticate_user_success(db_session):
    svc = AuthService(db_session)
    payload = UserCreate(email="login@example.com", password="StrongPass123!", full_name="Login", role="user")
    user = svc.signup(payload)

    # Mark email as verified for login tests
    from robbot.infra.persistence.repositories.credential_repository import CredentialRepository

    cred_repo = CredentialRepository(db_session)
    cred = cred_repo.get_by_user_id(user.id)
    cred.email_verified = True
    db_session.commit()

    token = svc.authenticate_user(payload.email, payload.password)
    assert token is not None
    assert isinstance(token.access_token, str)
    assert isinstance(token.refresh_token, str)


def test_refresh_rotation_revokes_used_token(db_session):
    svc = AuthService(db_session)
    payload = UserCreate(email="refresh@example.com", password="StrongPass123!", full_name="Refresh", role="user")
    user = svc.signup(payload)

    # Mark email as verified for login tests
    from robbot.infra.persistence.repositories.credential_repository import CredentialRepository

    cred_repo = CredentialRepository(db_session)
    cred = cred_repo.get_by_user_id(user.id)
    cred.email_verified = True
    db_session.commit()

    token = svc.authenticate_user(payload.email, payload.password)
    # Use refresh token once
    new_pair = svc.refresh(token.refresh_token)
    assert isinstance(new_pair.refresh_token, str)

    # Reuse original should fail (revoked)
    with pytest.raises(Exception):  # noqa: B017 (testing error handling)
        svc.refresh(token.refresh_token)


def test_signup_duplicate_email_error(db_session):
    svc = AuthService(db_session)
    payload = UserCreate(email="dup@example.com", password="StrongPass123!", full_name="Dup", role="user")
    svc.signup(payload)

    with pytest.raises(AuthException, match="User already exists"):
        svc.signup(payload)


def test_signup_weak_password_error(db_session):
    from pydantic import ValidationError

    from robbot.schemas.auth import SignupRequest

    # Pydantic validates before service, so expect ValidationError
    with pytest.raises(ValidationError):
        SignupRequest(email="weak@example.com", password="short", full_name="Weak")


def test_authenticate_user_wrong_password(db_session):
    svc = AuthService(db_session)
    payload = UserCreate(email="wrongpw@example.com", password="StrongPass123!", full_name="WrongPW", role="user")
    user = svc.signup(payload)

    cred_repo = CredentialRepository(db_session)
    cred = cred_repo.get_by_user_id(user.id)
    cred.email_verified = True
    db_session.commit()

    token = svc.authenticate_user(payload.email, "incorrect-password")
    assert token is None


def test_authenticate_user_nonexistent_user(db_session):
    svc = AuthService(db_session)

    token = svc.authenticate_user("missing@example.com", "irrelevant")

    assert token is None


def test_authenticate_user_email_not_verified(db_session):
    svc = AuthService(db_session)
    payload = UserCreate(email="unverified@example.com", password="StrongPass123!", full_name="Unverified", role="user")
    svc.signup(payload)

    with pytest.raises(AuthException, match="Email not verified"):
        svc.authenticate_user(payload.email, payload.password)


def test_refresh_with_revoked_token(db_session):
    svc = AuthService(db_session)
    payload = UserCreate(email="revoked@example.com", password="StrongPass123!", full_name="Revoked", role="user")
    user = svc.signup(payload)

    cred_repo = CredentialRepository(db_session)
    cred = cred_repo.get_by_user_id(user.id)
    cred.email_verified = True
    db_session.commit()

    token_pair = svc.authenticate_user(payload.email, payload.password)
    svc.token_repo.revoke(token_pair.refresh_token)

    with pytest.raises(AuthException, match="Token revoked"):
        svc.refresh(token_pair.refresh_token)


def test_refresh_with_expired_token(db_session):
    svc = AuthService(db_session)
    expired = security.create_token_for_subject("123", minutes=-1, token_type="refresh")

    with pytest.raises(AuthException, match="Token expired"):
        svc.refresh(expired)


def test_refresh_with_invalid_jti(db_session):
    svc = AuthService(db_session)
    invalid = security.create_token_for_subject("321", minutes=60, token_type="refresh", jti="missing-jti")

    with pytest.raises(AuthException, match="Session invalid or revoked"):
        svc.refresh(invalid)


def test_device_name_extracted_and_stored_on_login(db_session):
    svc = AuthService(db_session)
    payload = UserCreate(email="device@example.com", password="StrongPass123!", full_name="Device", role="user")
    user = svc.signup(payload)

    cred_repo = CredentialRepository(db_session)
    cred = cred_repo.get_by_user_id(user.id)
    cred.email_verified = True
    db_session.commit()

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"
    ip_address = "10.0.0.1"

    token = svc.authenticate_user(payload.email, payload.password, user_agent=user_agent, ip_address=ip_address)
    assert token is not None

    session_repo = svc.session_repo
    sessions = session_repo.get_all_by_user_id(user.id)
    assert len(sessions) == 1
    session = sessions[0]
    assert session.device_name == "Chrome on Windows"
    assert session.user_agent == user_agent
    assert session.ip_address == ip_address


def test_audit_log_on_successful_login(db_session):
    svc = AuthService(db_session)
    payload = UserCreate(email="audit@example.com", password="StrongPass123!", full_name="Audit", role="user")
    user = svc.signup(payload)

    cred_repo = CredentialRepository(db_session)
    cred = cred_repo.get_by_user_id(user.id)
    cred.email_verified = True
    db_session.commit()

    svc.authenticate_user(payload.email, payload.password)

    audit_logs = db_session.query(AuditLogModel).all()
    assert len(audit_logs) == 1
    assert audit_logs[0].action == "login_success"
    assert audit_logs[0].entity_id == str(user.id)

