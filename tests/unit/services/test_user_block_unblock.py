import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from robbot.services.user_service import UserService
from robbot.schemas.user import UserCreate
from robbot.infra.db.models.user_model import UserModel
from robbot.infra.db.models.auth_session_model import AuthSessionModel
from robbot.adapters.repositories.user_repository import UserRepository


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    # Minimal tables for this test
    UserModel.__table__.create(bind=engine)
    AuthSessionModel.__table__.create(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def make_user(db_session):
    repo = UserRepository(db_session)
    payload = UserCreate(email="adminblock@example.com", password="StrongPass123!", full_name="Admin Block", role="user")
    # Create user with legacy hash path
    from robbot.core import security
    hashed = security.get_password_hash(payload.password)
    return repo.create_user(payload, hashed)


def test_block_user_revokes_sessions_and_sets_inactive(db_session):
    service = UserService(db_session)
    user = make_user(db_session)

    # Create two active sessions for the user
    from datetime import UTC, datetime, timedelta
    expires = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=30)
    s1 = AuthSessionModel(user_id=user.id, refresh_token_jti="blk-jti-1", ip_address="127.0.0.1", user_agent="UA", device_name="PC", expires_at=expires)
    s2 = AuthSessionModel(user_id=user.id, refresh_token_jti="blk-jti-2", ip_address="127.0.0.1", user_agent="UA", device_name="PC", expires_at=expires)
    db_session.add_all([s1, s2])
    db_session.commit()

    out = service.block_user(user.id, reason="policy_violation")
    assert out.is_active is False

    sessions = db_session.query(AuthSessionModel).filter(AuthSessionModel.user_id == user.id).all()
    assert all(s.is_revoked for s in sessions)


def test_unblock_user_sets_active(db_session):
    service = UserService(db_session)
    user = make_user(db_session)
    # Block first
    service.block_user(user.id, reason="policy_violation")

    out = service.unblock_user(user.id, reason="appeal_accepted")
    assert out.is_active is True
