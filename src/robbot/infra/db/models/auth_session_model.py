"""Model ORM para sessões de autenticação de usuários.

Permite gerenciamento de sessões, permitindo aos usuários visualizar e revogar sessões ativas.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from robbot.infra.db.base import Base


class AuthSessionModel(Base):
    """Sessões de autenticação de usuário (JWT + metadados).

    Esta tabela armazena metadados sobre sessões ativas de usuários, permitindo:
    - Listar todas as sessões ativas (web, mobile, etc.)
    - Revogar sessões específicas (logout de dispositivo específico)
    - Revogar todas as sessões (logout de todos os dispositivos)
    - Rastrear fingerprint de dispositivo (IP + User-Agent)
    - Detectar atividade suspeita (nova localização, novo dispositivo)

    Observações:
    - Sessões são criadas no login
    - Sessões são atualizadas no refresh de token (last_used_at)
    - Sessões são marcadas como revogadas no logout ou revogação explícita
    - Sessões expiradas podem ser limpas por um job em background
    """

    __tablename__ = "auth_sessions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key to User
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Refresh Token (JWT ID)
    refresh_token_jti = Column(String(255), unique=True, nullable=False, index=True)

    # Device Information
    device_name = Column(String(255), nullable=True)  # e.g., "Chrome on Windows 10"
    ip_address = Column(String(45), nullable=False)  # IPv4 (15 chars) or IPv6 (45 chars)
    user_agent = Column(Text, nullable=True)

    # Session Lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Revocation
    is_revoked = Column(Boolean, default=False, nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revocation_reason = Column(
        String(255), nullable=True
    )  # e.g., "logout", "password_changed", "admin_action"

    # Relationships
    user = relationship("UserModel", back_populates="auth_sessions")

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<AuthSessionModel(id={self.id}, user_id={self.user_id}, device={self.device_name}, revoked={self.is_revoked})>"

    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now(self.expires_at.tzinfo) > self.expires_at

    @property
    def is_active(self) -> bool:
        """Check if session is active (not revoked and not expired)."""
        return not self.is_revoked and not self.is_expired
