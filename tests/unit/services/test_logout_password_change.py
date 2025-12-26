import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from robbot.services.auth_services import AuthService
from robbot.schemas.user import UserCreate
from robbot.services.credential_service import CredentialService
from robbot.infra.db.models.user_model import UserModel
from robbot.infra.db.models.credential_model import CredentialModel
from robbot.infra.db.models.revoked_token_model import RevokedTokenModel
from robbot.infra.db.models.auth_session_model import AuthSessionModel


@pytest.fixture()
def db_session():
    # In-memory SQLite for fast tests
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    # Create tables required for these flows
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


def test_logout_revokes_tokens_and_session(db_session):
    svc = AuthService(db_session)
    payload = UserCreate(email="logout@example.com", password="StrongPass123!", full_name="Logout", role="user")
    user = svc.signup(payload)

    # Mark email as verified for login tests
    from robbot.adapters.repositories.credential_repository import CredentialRepository
    cred_repo = CredentialRepository(db_session)
    cred = cred_repo.get_by_user_id(user.id)
    cred.email_verified = True
    db_session.commit()

    # Login to create tokens and session
    token = svc.authenticate_user(payload.email, payload.password)
    assert token is not None

    # The service stores session on authenticate_user; just sanity check one exists
    sess = db_session.query(AuthSessionModel).filter(AuthSessionModel.user_id == user.id).first()
    assert sess is not None
    assert sess.is_revoked is False

    # Perform logout
    svc.logout(user_id=user.id, access_token=token.access_token, refresh_token=token.refresh_token)

    # Tokens should be persisted as revoked
    revoked = db_session.query(RevokedTokenModel).all()
    assert len(revoked) >= 2
    tokens = {r.token for r in revoked}
    assert token.access_token in tokens
    assert token.refresh_token in tokens

    # Session should be revoked
    sess = db_session.query(AuthSessionModel).filter(AuthSessionModel.id == sess.id).first()
    assert sess.is_revoked is True
    assert sess.revocation_reason == "logout"


def test_change_password_updates_credential_and_revokes_sessions(db_session):
    svc = AuthService(db_session)
    payload = UserCreate(email="changepw@example.com", password="Initial123!", full_name="ChangePW", role="user")
    user = svc.signup(payload)

    # Create two active sessions for the user
    from datetime import UTC, datetime, timedelta
    expires = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=30)
    s1 = AuthSessionModel(user_id=user.id, refresh_token_jti="cpw-jti-1", ip_address="127.0.0.1", user_agent="UA", device_name="PC", expires_at=expires)
    s2 = AuthSessionModel(user_id=user.id, refresh_token_jti="cpw-jti-2", ip_address="127.0.0.1", user_agent="UA", device_name="PC", expires_at=expires)
    db_session.add_all([s1, s2])
    db_session.commit()

    # Change password
    svc.change_password(user_id=user.id, old_password="Initial123!", new_password="NewPass456!")

    # Verify credential updated
    cred_svc = CredentialService(db_session)
    assert cred_svc.verify_password(user.id, "NewPass456!") is True
    assert cred_svc.verify_password(user.id, "Initial123!") is False

    # Sessions revoked
    sess = db_session.query(AuthSessionModel).filter(AuthSessionModel.user_id == user.id).all()
    assert len(sess) == 2
    assert all(s.is_revoked for s in sess)
