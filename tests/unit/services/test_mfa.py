"""Testes unitários para MFA (FASE 5)."""

import base64
import json
import pytest
import pyotp
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from robbot.services.mfa_service import MfaService
from robbot.services.auth_services import AuthService
from robbot.adapters.repositories.credential_repository import CredentialRepository
from robbot.core.exceptions import AuthException
from robbot.schemas.auth import SignupRequest


@pytest.fixture
def db_session():
    """Cria DB SQLite em memória com tabelas mínimas."""
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text(
            """
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
            """
        ))
        conn.execute(text(
            """
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
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
            """
        ))
        conn.commit()
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_setup_mfa_and_verify_totp(db_session):
    auth_service = AuthService(db_session)
    mfa_service = MfaService(db_session)
    cred_repo = CredentialRepository(db_session)

    # cria usuário
    user = auth_service.signup(SignupRequest(
        email="mfa@example.com",
        password="SecurePass123!",
        full_name="MFA User"
    ))

    # habilita MFA
    secret, qr_b64, codes = mfa_service.setup_mfa(user.id)
    assert isinstance(secret, str) and len(secret) >= 16
    assert isinstance(qr_b64, str) and len(qr_b64) > 0
    assert isinstance(codes, list) and len(codes) == 10

    # verifica que credencial está habilitada
    cred = cred_repo.get_by_user_id(user.id)
    assert cred.mfa_enabled is True
    assert cred.mfa_secret == secret
    assert isinstance(cred.backup_codes, str)
    hashed_list = json.loads(cred.backup_codes)
    assert len(hashed_list) == 10

    # verifica TOTP válido
    code = pyotp.TOTP(secret).now()
    assert mfa_service.verify_mfa(user.id, code) is True

    # verifica TOTP inválido
    with pytest.raises(AuthException, match="Invalid MFA code"):
        mfa_service.verify_mfa(user.id, "000000")


def test_backup_code_consumption(db_session):
    auth_service = AuthService(db_session)
    mfa_service = MfaService(db_session)
    cred_repo = CredentialRepository(db_session)

    user = auth_service.signup(SignupRequest(
        email="backup@example.com",
        password="SecurePass123!",
        full_name="Backup User"
    ))

    secret, qr_b64, codes = mfa_service.setup_mfa(user.id)
    first_code = codes[0]

    # usa primeiro backup code
    assert mfa_service.verify_backup_code(user.id, first_code) is True

    # tentar reutilizar deve falhar
    with pytest.raises(AuthException, match="Invalid backup code"):
        mfa_service.verify_backup_code(user.id, first_code)

    # ainda deve existir 9 códigos
    cred = cred_repo.get_by_user_id(user.id)
    remaining = json.loads(cred.backup_codes)
    assert len(remaining) == 9
