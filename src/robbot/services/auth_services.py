"""Serviço de autenticação implementando registro, login, refresh e revogação de tokens.

Responsabilidades:
- Gerenciar ciclo de vida de usuários (signup)
- Autenticar credenciais e emitir tokens JWT
- Renovar tokens (refresh)
- Gerenciar sessões de usuário
- Integração com MFA e verificação de email
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from robbot.adapters.repositories.auth_session_repository import AuthSessionRepository
from robbot.adapters.repositories.token_repository import TokenRepository
from robbot.adapters.repositories.user_repository import UserRepository
from robbot.common.utils import send_email
from robbot.core import security
from robbot.core.exceptions import AuthException
from robbot.schemas.token import Token
from robbot.schemas.auth import SignupRequest
from robbot.services.email_verification_service import EmailVerificationService
from robbot.schemas.user import UserOut
from robbot.services.credential_service import CredentialService
from datetime import UTC, datetime
from robbot.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class AuthService:
    """Camada de serviço que implementa regras de negócio de autenticação.
    
    Gerencia autenticação de usuários, emissão de tokens, sessões,
    e integração com MFA e verificação de email.
    """

    def __init__(self, db: Session):
        self.repo = UserRepository(db)
        self.token_repo = TokenRepository(db)
        self.credential_svc = CredentialService(db)
        self.session_repo = AuthSessionRepository(db)
        self.audit_svc = AuditService(db)
        self.email_verification_svc = EmailVerificationService(db)

    def signup(self, payload: SignupRequest) -> UserOut:
        """Registra um novo usuário com validação de senha e persistência.
        
        Args:
            payload: Dados de registro incluindo email, senha e nome completo
            
        Returns:
            Dados do usuário criado (sem senha)
            
        Raises:
            AuthException: Se usuário já existe ou senha é inválida
            
        Note:
            Cria usuário com email_verified=false. Verificação de email 
            é necessária antes do login.
        """
        existing = self.repo.get_by_email(payload.email)
        if existing:
            raise AuthException("User already exists")
        security.validate_password_policy(payload.password)
        
        from robbot.schemas.user import UserCreate
        user_data = UserCreate(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            role=payload.role
        )
        hashed = security.get_password_hash(payload.password)
        user = self.repo.create_user(user_data, hashed)
        
        self.credential_svc.set_password(user.id, payload.password)
        
        verification_token = self.email_verification_svc.generate_verification_token(user.id)
        
        logger.info(f"User registered: {user.email} (verification token: {verification_token[:8]}...)")
        
        return UserOut.model_validate(user)

    def authenticate_user(
        self,
        email: str,
        password: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> Optional[Token]:
        """Valida credenciais e retorna tokens com dados do usuário.
        
        Bloqueia login se email não verificado.
        Se MFA habilitado, retorna tokens temporários com mfa_required=True.
        Se MFA desabilitado, retorna tokens finais com mfa_required=False.
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            user_agent: User-agent do dispositivo (opcional)
            ip_address: Endereço IP do cliente (opcional)
        
        Returns:
            Token com mfa_required=True se MFA habilitado (tokens temporários)
            Token com mfa_required=False se MFA desabilitado (tokens finais)
            None se credenciais inválidas ou usuário inativo
        """
        user = self.repo.get_by_email(email)
        if not user:
            logger.warning(f"Login failed: user not found for email {email}")
            return None
        if not user.is_active:
            logger.warning(f"Login failed: user {email} is inactive")
            return None
        
        if not self.email_verification_svc.is_email_verified(user.id):
            logger.warning(f"Login failed: email not verified for user {email}")
            raise AuthException("Email not verified. Please check your email for verification link.")
        
        
        # Verificar senha via CredentialService
        if not self.credential_svc.verify_password(user.id, password):
            logger.warning(f"Login failed: invalid password for user {email}")
            try:
                self.audit_svc.log_action(
                    action="login_failure",
                    entity_type="User",
                    entity_id="unknown",
                    user_id=None,
                    old_value={"email": email},
                )
            except SQLAlchemyError:
                logger.warning("Audit log failed for login_failure")
            return None
        
        from robbot.adapters.repositories.credential_repository import CredentialRepository
        credential_repo = CredentialRepository(self.repo.db)
        credential = credential_repo.get_by_user_id(user.id)
        mfa_enabled = credential.mfa_enabled if credential else False
        
        if mfa_enabled:
            # Return temporary tokens that require MFA verification
            logger.info(f"Login successful (MFA required): user {email} (id={user.id})")
            # Create temporary tokens with short expiration (5 minutes)
            temporary_tokens = security.create_token_for_subject(
                str(user.id), 
                minutes=5, 
                token_type="mfa-pending"
            )
            # Don't create session yet - will be created after MFA verification
            return Token(
                access_token=temporary_tokens,
                refresh_token="",  # No refresh token until MFA verified
                mfa_required=True,
                user=user
            )
        
        # Normal login flow (MFA disabled)
        logger.info(f"Login successful: user {email} (id={user.id})")
        try:
            self.audit_svc.log_action(
                action="login_success",
                entity_type="User",
                entity_id=str(user.id),
                user_id=user.id,
                new_value={"email": email},
            )
        except SQLAlchemyError:
            logger.warning("Audit log failed for login_success")
        tokens = security.create_access_refresh_tokens(str(user.id))
        # Criar sessão atrelada ao JTI do refresh
        payload = security.decode_token(tokens["refresh_token"], verify_exp=True)
        jti = payload.get("jti")
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp, UTC) if isinstance(exp, (int, float)) else datetime.now(UTC)
        device_name = security.parse_device_name(user_agent)
        self.session_repo.create(
            user_id=user.id,
            refresh_token_jti=jti,
            ip_address=ip_address or "unknown",
            user_agent=user_agent or "unknown",
            device_name=device_name,
            expires_at=expires_at,
        )
        return Token(**tokens, user=user)  # Include user object for cookie strategy

    def refresh(
        self,
        refresh_token: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> Token:
        """Rotação de refresh token: valida, revoga o token usado e retorna novo par.
        
        Args:
            refresh_token: Token de refresh a ser renovado
            user_agent: User-agent do dispositivo (opcional)
            ip_address: Endereço IP do cliente (opcional)
            
        Returns:
            Novo par de tokens (access + refresh)
            
        Raises:
            AuthException: Se token inválido, revogado ou expirado
        """
        # Bloquear reuso de refresh (rotation)
        if self.token_repo.is_revoked(refresh_token):
            raise AuthException("Token revoked")
        payload = security.decode_token(refresh_token, verify_exp=True)
        if payload.get("type") != "refresh":
            raise AuthException("Invalid token type")
        subject = payload.get("sub")
        # Validar sessão via JTI
        jti = payload.get("jti")
        sess = self.session_repo.get_by_jti(jti)
        if not sess or sess.is_revoked or sess.is_expired:
            raise AuthException("Session invalid or revoked")
        # Atualizar metadados da sessão (last_used + device info se fornecido)
        device_name = security.parse_device_name(user_agent) if user_agent else None
        self.session_repo.update_last_used(
            sess,
            user_agent=user_agent,
            ip_address=ip_address,
            device_name=device_name,
        )
        # Revogar o refresh token utilizado
        self.token_repo.revoke(refresh_token)
        tokens = security.create_access_refresh_tokens(subject)
        try:
            self.audit_svc.log_action(
                action="token_refresh",
                entity_type="User",
                entity_id=str(subject),
                user_id=int(subject) if subject else None,
            )
        except SQLAlchemyError:
            logger.warning("Audit log failed for token_refresh")
        return Token(**tokens)

    def revoke_token(self, token: str) -> None:
        """
        Revoke token (refresh or access) by persisting it to DB.
        """
        self.token_repo.revoke(token)
        logger.info(f"Token revoked successfully")

    def logout(
        self,
        user_id: int,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> None:
        """
        Logout current session: revoke provided tokens and mark session revoked.
        Also writes an audit log entry for logout.

        Args:
            user_id: ID of the user performing logout
            access_token: Optional access token string (will be revoked if provided)
            refresh_token: Optional refresh token string (will be revoked and used to revoke session)
        """
        # Revoke tokens if provided
        if access_token:
            self.token_repo.revoke(access_token)
        if refresh_token:
            # Revoke the refresh token itself
            self.token_repo.revoke(refresh_token)
            # Revoke the associated session via JTI
            try:
                payload = security.decode_token(refresh_token, verify_exp=False)
            except AuthException:
                payload = {}
            if payload.get("type") == "refresh":
                jti = payload.get("jti")
                sess = self.session_repo.get_by_jti(jti) if jti else None
                if sess and not sess.is_revoked:
                    self.session_repo.revoke(sess, reason="logout")

        # Audit
        try:
            self.audit_svc.log_action(
                action="logout",
                entity_type="User",
                entity_id=str(user_id),
                user_id=user_id,
            )
        except SQLAlchemyError:
            logger.warning("Audit log failed for logout")

    def send_password_recovery(self, email: str) -> None:
        """
        Generates a short-lived token and sends to email. Token is a JWT with type 'pw-reset'.
        """
        user = self.repo.get_by_email(email)
        if not user:
            return
        token = security.create_token_for_subject(
            str(user.id), minutes=15, token_type="pw-reset")
        send_email(to=email, subject="Password recovery",
                   body=f"Use this token to reset: {token}")

    def reset_password(self, token: str, new_password: str) -> None:
        """Redefine senha se token válido e senha atende política.
        
        Args:
            token: Token de redefinição de senha
            new_password: Nova senha do usuário
            
        Raises:
            AuthException: Se token inválido ou senha não atende política
        """
        payload = security.decode_token(token, verify_exp=True)
        if payload.get("type") != "pw-reset":
            raise AuthException("Invalid token for password reset")
        user_id = payload.get("sub")
        if not user_id:
            raise AuthException("Invalid token")
        user = self.repo.get_by_id(int(user_id))
        if not user:
            raise AuthException("User not found")
        
        security.validate_password_policy(new_password)
        # Atualizar via service
        self.credential_svc.set_password(user.id, new_password)
        # Revogar todas as sessões ativas após troca de senha
        self.session_repo.revoke_all_for_user(user.id, reason="password_reset")
        try:
            self.audit_svc.log_action(
                action="password_reset",
                entity_type="User",
                entity_id=str(user.id),
                user_id=user.id,
            )
        except SQLAlchemyError:
            logger.warning("Audit log failed for password_reset")

    def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        """
        Change password for authenticated user, verifying current password first.

        - Verifies the old password using CredentialService
        - Validates policy and sets the new password
        - Revokes all active sessions for the user (security best practice)
        - Logs audit event "password_change"
        """
        user = self.repo.get_by_id(int(user_id))
        if not user:
            raise AuthException("User not found")

        # Verify current password
        if not self.credential_svc.verify_password(user.id, old_password):
            raise AuthException("Invalid current password")

        # Validate and set new password
        security.validate_password_policy(new_password)
        self.credential_svc.set_password(user.id, new_password)

        # Revoke all sessions after password change
        self.session_repo.revoke_all_for_user(user.id, reason="password_changed")

        # Audit
        try:
            self.audit_svc.log_action(
                action="password_change",
                entity_type="User",
                entity_id=str(user.id),
                user_id=user.id,
            )
        except SQLAlchemyError:
            logger.warning("Audit log failed for password_change")

    def verify_mfa_and_complete_login(
        self,
        temporary_token: str,
        code: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> Token:
        """Completa login após verificação MFA.
        
        Args:
            temporary_token: Token temporário do login inicial
            code: Código TOTP ou código de backup
            user_agent: User-agent para rastreamento de sessão (opcional)
            ip_address: Endereço IP para rastreamento de sessão (opcional)
            
        Returns:
            Token with final access and refresh tokens
            
        Raises:
            AuthException: If token invalid, expired, or MFA verification fails
        """
        # Validate temporary token
        try:
            payload = security.decode_token(temporary_token, verify_exp=True)
        except AuthException as e:
            logger.warning(f"MFA login failed: invalid temporary token - {e}")
            raise AuthException("Invalid or expired temporary token")
        
        if payload.get("type") != "mfa-pending":
            raise AuthException("Invalid token type for MFA verification")
        
        user_id = payload.get("sub")
        if not user_id:
            raise AuthException("Invalid token")
        
        user = self.repo.get_by_id(int(user_id))
        if not user:
            raise AuthException("User not found")
        
        # Verify MFA code
        from robbot.services.mfa_service import MfaService
        mfa_service = MfaService(self.repo.db)
        
        # Try TOTP first, then backup code
        verified = mfa_service.verify_mfa(user.id, code)
        if not verified:
            verified = mfa_service.verify_backup_code(user.id, code)
        
        if not verified:
            logger.warning(f"MFA verification failed for user {user.email}")
            try:
                self.audit_svc.log_action(
                    action="mfa_verification_failed",
                    entity_type="User",
                    entity_id=str(user.id),
                    user_id=user.id,
                )
            except SQLAlchemyError:
                logger.warning("Audit log failed for mfa_verification_failed")
            raise AuthException("Invalid MFA code")
        
        # MFA verified - create final tokens and session
        logger.info(f"MFA verification successful: user {user.email} (id={user.id})")
        try:
            self.audit_svc.log_action(
                action="mfa_login_success",
                entity_type="User",
                entity_id=str(user.id),
                user_id=user.id,
                new_value={"email": user.email},
            )
        except SQLAlchemyError:
            logger.warning("Audit log failed for mfa_login_success")
        
        tokens = security.create_access_refresh_tokens(str(user.id))
        
        # Create session
        payload = security.decode_token(tokens["refresh_token"], verify_exp=True)
        jti = payload.get("jti")
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp, UTC) if isinstance(exp, (int, float)) else datetime.now(UTC)
        device_name = security.parse_device_name(user_agent)
        self.session_repo.create(
            user_id=user.id,
            refresh_token_jti=jti,
            ip_address=ip_address or "unknown",
            user_agent=user_agent or "unknown",
            device_name=device_name,
            expires_at=expires_at,
        )
        
        return Token(**tokens, user=user)
