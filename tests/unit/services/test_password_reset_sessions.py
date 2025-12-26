import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from robbot.services.auth_services import AuthService
from robbot.schemas.user import UserCreate
from robbot.infra.db.models.user_model import UserModel
from robbot.infra.db.models.credential_model import CredentialModel
from robbot.infra.db.models.auth_session_model import AuthSessionModel
from robbot.core import security
from datetime import UTC, datetime, timedelta


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    # Create needed tables
    UserModel.__table__.create(bind=engine)
    CredentialModel.__table__.create(bind=engine)
    AuthSessionModel.__table__.create(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_reset_password_revokes_sessions(db_session):
    svc = AuthService(db_session)
    payload = UserCreate(email="reset@example.com", password="StrongPass123!", full_name="Reset", role="user")
    user = svc.signup(payload)

    # Create two active sessions for the user
    expires = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=30)
    s1 = AuthSessionModel(user_id=user.id, refresh_token_jti="jti1", ip_address="127.0.0.1", user_agent="UA", device_name="PC", expires_at=expires)
    s2 = AuthSessionModel(user_id=user.id, refresh_token_jti="jti2", ip_address="127.0.0.1", user_agent="UA", device_name="PC", expires_at=expires)
    db_session.add_all([s1, s2])
    db_session.commit()

    # Generate a password reset token
    token = security.create_token_for_subject(str(user.id), minutes=15, token_type="pw-reset")

    # Perform reset
    svc.reset_password(token, "NewPass456!")

    # Reload sessions and assert revoked
    sess = db_session.query(AuthSessionModel).filter(AuthSessionModel.user_id == user.id).all()
    assert all(s.is_revoked for s in sess)
