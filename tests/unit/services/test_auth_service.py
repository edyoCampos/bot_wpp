import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from robbot.services.auth_services import AuthService
from robbot.schemas.user import UserCreate
from robbot.infra.db.models.user_model import UserModel
from robbot.infra.db.models.credential_model import CredentialModel
from robbot.infra.db.models.revoked_token_model import RevokedTokenModel
from robbot.infra.db.models.auth_session_model import AuthSessionModel
from robbot.adapters.repositories.credential_repository import CredentialRepository


@pytest.fixture()
def db_session():
    # Use in-memory SQLite for fast unit testing
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    # Create only required tables to avoid enum/type issues
    UserModel.__table__.create(bind=engine)
    CredentialModel.__table__.create(bind=engine)
    RevokedTokenModel.__table__.create(bind=engine)
    AuthSessionModel.__table__.create(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
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
    from robbot.adapters.repositories.credential_repository import CredentialRepository
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
    from robbot.adapters.repositories.credential_repository import CredentialRepository
    cred_repo = CredentialRepository(db_session)
    cred = cred_repo.get_by_user_id(user.id)
    cred.email_verified = True
    db_session.commit()

    token = svc.authenticate_user(payload.email, payload.password)
    # Use refresh token once
    new_pair = svc.refresh(token.refresh_token)
    assert isinstance(new_pair.refresh_token, str)

    # Reuse original should fail (revoked)
    with pytest.raises(Exception):
        svc.refresh(token.refresh_token)
