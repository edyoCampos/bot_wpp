"""Model ORM para credenciais de autenticação de usuários.

Separa credenciais de autenticação dos dados de perfil do usuário,
seguindo o Princípio de Separação de Responsabilidades de Segurança.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from robbot.infra.db.base import Base


class CredentialModel(Base):
    """Credenciais de autenticação do usuário (separadas do perfil).

    Esta tabela contém todos os dados relacionados à autenticação,
    completamente separados das informações de perfil do usuário.

    Justificativa:
    - User é uma entidade de domínio (preocupação de negócio)
    - Credential é uma entidade de segurança (preocupação de infraestrutura)
    - Esta separação permite:
      * Consultas de usuário sem expor credenciais
      * Suporte para múltiplos métodos de auth (SSO, OAuth, magic links)
      * Auditoria granular de mudanças de senha
      * Melhor performance (consultas de user não fazem join com credentials)
    """

    __tablename__ = "credentials"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key to User (1:1 relationship)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )

    # Password Authentication
    hashed_password = Column(String(255), nullable=False)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)

    # Email Verification
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_sent_at = Column(DateTime(timezone=True), nullable=True)

    # Password Reset
    reset_token = Column(String(255), nullable=True, index=True)
    reset_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    reset_token_used = Column(Boolean, default=False)

    # MFA (Multi-Factor Authentication)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(255), nullable=True)  # TOTP secret (encrypted)
    backup_codes = Column(Text, nullable=True)  # JSON array of hashed backup codes

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("UserModel", back_populates="credential", uselist=False)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<CredentialModel(user_id={self.user_id}, email_verified={self.email_verified}, mfa_enabled={self.mfa_enabled})>"
