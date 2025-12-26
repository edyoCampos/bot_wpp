"""Serviço de Autenticação Multi-Fator (MFA).

Implementa fluxo de MFA com TOTP (pyotp) e códigos de backup.
"""

import base64
import json
import secrets
from typing import Tuple

import pyotp
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from robbot.core.exceptions import AuthException
from robbot.adapters.repositories.credential_repository import CredentialRepository
from robbot.adapters.repositories.user_repository import UserRepository


class MfaService:
    """Serviço para habilitar, verificar e desabilitar MFA."""

    def __init__(self, db: Session, issuer: str = "Bot WPP"):
        self.db = db
        self.credential_repo = CredentialRepository(db)
        self.user_repo = UserRepository(db)
        self.issuer = issuer

    def _generate_secret(self) -> str:
        """Gera segredo base32 para TOTP."""
        return pyotp.random_base32()

    def _otpauth_uri(self, email: str, secret: str) -> str:
        """Cria URI otpauth:// para apps de MFA."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=self.issuer)

    def _generate_backup_codes(self, count: int = 10) -> Tuple[list[str], str]:
        """Gera códigos de backup (retorna plain + JSON com hashes)."""
        codes: list[str] = []
        hashed: list[str] = []
        for _ in range(count):
            code = secrets.token_hex(4)  # 8 hex chars
            codes.append(code)
            hashed.append(bcrypt.hash(code))
        return codes, json.dumps(hashed)

    def setup_mfa(self, user_id: int) -> Tuple[str, str, list[str]]:
        """Habilita MFA para usuário e retorna (secret, qr_code_base64, backup_codes)."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise AuthException("User not found")

        secret = self._generate_secret()
        uri = self._otpauth_uri(user.email, secret)
        # Para MVP, codificamos a URI como base64 (placeholder de imagem)
        qr_code_base64 = base64.b64encode(uri.encode()).decode()

        codes, hashed_json = self._generate_backup_codes()
        self.credential_repo.enable_mfa(
            credential=self.credential_repo.get_by_user_id(user_id),
            secret=secret,
            backup_codes=hashed_json,
        )
        return secret, qr_code_base64, codes

    def verify_mfa(self, user_id: int, code: str) -> bool:
        """Verifica código TOTP. Lança AuthException em falha."""
        credential = self.credential_repo.get_by_user_id(user_id)
        if not credential or not credential.mfa_enabled or not credential.mfa_secret:
            raise AuthException("MFA not enabled")
        totp = pyotp.TOTP(credential.mfa_secret)
        if not totp.verify(code, valid_window=1):
            raise AuthException("Invalid MFA code")
        return True

    def verify_backup_code(self, user_id: int, code: str) -> bool:
        """Verifica e consome um backup code. Lança AuthException se inválido."""
        credential = self.credential_repo.get_by_user_id(user_id)
        if not credential or not credential.mfa_enabled:
            raise AuthException("MFA not enabled")
        if not credential.backup_codes:
            raise AuthException("No backup codes")
        hashed_list: list[str] = json.loads(credential.backup_codes)
        # Procura correspondente
        match_index = None
        for i, h in enumerate(hashed_list):
            if bcrypt.verify(code, h):
                match_index = i
                break
        if match_index is None:
            raise AuthException("Invalid backup code")
        # Consome código (remove)
        hashed_list.pop(match_index)
        credential.backup_codes = json.dumps(hashed_list)
        self.db.add(credential)
        self.db.commit()
        return True

    def disable_mfa(self, user_id: int) -> None:
        """Desabilita MFA para usuário."""
        credential = self.credential_repo.get_by_user_id(user_id)
        if not credential:
            raise AuthException("Credential not found")
        self.credential_repo.disable_mfa(credential)
