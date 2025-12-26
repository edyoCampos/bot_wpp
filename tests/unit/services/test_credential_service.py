import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from robbot.services.credential_service import CredentialService
from robbot.infra.db.models.credential_model import CredentialModel


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    CredentialModel.__table__.create(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_set_and_verify_password(db_session):
    svc = CredentialService(db_session)
    user_id = 100

    # set password
    svc.set_password(user_id, "StrongPass123!")

    # verify
    assert svc.verify_password(user_id, "StrongPass123!") is True
    assert svc.verify_password(user_id, "WrongPass!") is False


def test_change_password(db_session):
    svc = CredentialService(db_session)
    user_id = 101

    svc.set_password(user_id, "Initial123!")

    # change
    svc.change_password(user_id, "Initial123!", "NewPass456!")

    # verify new
    assert svc.verify_password(user_id, "NewPass456!") is True
