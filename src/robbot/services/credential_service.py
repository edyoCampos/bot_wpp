"""Serviço para gerenciamento de credenciais de autenticação.

Responsabilidades:
- set_password(user_id, password): define/atualiza senha com política de segurança
- verify_password(user_id, password): verifica senha contra hash armazenado
- change_password(user_id, old_password, new_password): troca segura de senha

Utiliza CredentialRepository para persistência e security helpers para hashing.
"""

from sqlalchemy.orm import Session

from robbot.adapters.repositories.credential_repository import CredentialRepository
from robbot.core import security
from robbot.core.exceptions import AuthException


class CredentialService:
    """Service para operações de credenciais de autenticação."""

    def __init__(self, db: Session):
        self.repo = CredentialRepository(db)

    def set_password(self, user_id: int, password: str) -> None:
        """Define ou atualiza a senha de um usuário.

        - Valida política
        - Gera hash bcrypt
        - Cria credencial se não existir, senão atualiza
        """
        security.validate_password_policy(password)
        hashed = security.get_password_hash(password)
        cred = self.repo.get_by_user_id(user_id)
        if not cred:
            self.repo.create(user_id, hashed)
        else:
            self.repo.update_password(cred, hashed)

    def verify_password(self, user_id: int, password: str) -> bool:
        """Verifica senha contra o hash armazenado."""
        cred = self.repo.get_by_user_id(user_id)
        if not cred:
            raise AuthException("Credencial não encontrada")
        return security.verify_password(password, cred.hashed_password)

    def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        """Troca de senha com verificação do password atual."""
        cred = self.repo.get_by_user_id(user_id)
        if not cred:
            raise AuthException("Credencial não encontrada")
        if not security.verify_password(old_password, cred.hashed_password):
            raise AuthException("Senha atual inválida")
        self.set_password(user_id, new_password)
