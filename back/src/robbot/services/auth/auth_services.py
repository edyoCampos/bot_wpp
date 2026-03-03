"""Authentication service implementing registration, login, refresh, and token revocation.

Responsibilities:
- Manage user lifecycle (signup)
- Authenticate credentials and issue JWT tokens
- Renew tokens (refresh)
- Manage user sessions
- Integration with MFA and email verification
"""

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.auth_session_repository import AuthSessionRepository
from robbot.infra.persistence.repositories.token_repository import TokenRepository
from robbot.infra.persistence.repositories.user_repository import UserRepository
from robbot.common.utils import send_email
from robbot.config.settings import settings
from robbot.core import security
from robbot.core.custom_exceptions import AuthException
from robbot.schemas.auth import SignupRequest
from robbot.schemas.token import Token
from robbot.schemas.user import UserOut
from robbot.services.auth.audit_service import AuditService
from robbot.services.auth.credential_service import CredentialService
from robbot.services.auth.email_verification_service import EmailVerificationService
from robbot.services.auth.mfa_service import MfaService

logger = logging.getLogger(__name__)


class AuthService:
    """Service layer implementing authentication business rules.

    Manages user authentication, token issuance, sessions,
    and integration with MFA and email verification.
    """

    def __init__(self, db: Session):
        self.repo = UserRepository(db)
        self.token_repo = TokenRepository(db)
        self.credential_svc = CredentialService(db)
        self.session_repo = AuthSessionRepository(db)
        self.audit_svc = AuditService(db)
        self.email_verification_svc = EmailVerificationService(db)
        self.mfa_service = MfaService(db)

    def signup(self, payload: SignupRequest) -> UserOut:
        """Registers a new user with password validation and persistence.

        Args:
            payload: Registration data including email, password, and full name

        Returns:
            Created user data (without password)

        Raises:
            AuthException: If user already exists or password is invalid

        Note:
            Creates user with email_verified=false. Email verification
            is required before login.
        """
        existing = self.repo.get_by_email(payload.email)
        if existing:
            raise AuthException("User already exists")
        security.validate_password_policy(payload.password)

        from robbot.schemas.user import UserCreate

        user_data = UserCreate(
            email=payload.email, password=payload.password, full_name=payload.full_name, role=payload.role
        )
        hashed = security.get_password_hash(payload.password)
        user = self.repo.create_user(user_data, hashed)

        self.credential_svc.set_password(user.id, payload.password)

        verification_token = self.email_verification_svc.generate_verification_token(user.id)

        logger.info("[INFO] User registered: %s (verification token: %s...)", user.email, verification_token[:8])

        # Stylized verification email (HTML) - GO Robot branding
        # Note: Keeping email body in Portuguese as it is user-facing
        verification_link = f"http://localhost:3333/api/v1/auth/email/verify?token={verification_token}"
        email_body = f"""
<html>
    <body style="background: #FAFAFA; font-family: 'Geist', 'Lora', Arial, sans-serif; color: #1F2937; margin:0; padding:0;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background: #FAFAFA; padding: 32px 0;">
            <tr>
                <td align="center">
                    <table width="420" cellpadding="0" cellspacing="0" style="background: #fff; border-radius: 18px; box-shadow: 0 4px 32px 0 #5473E81A; padding: 32px; border: 1px solid #E5E7EB;">
                        <tr>
                            <td align="center" style="padding-bottom: 16px;">
                                <img src='http://localhost:3000/assets/go_robot.png' alt='GO Robot' width='140' height='140' style='border-radius:24px; margin-bottom:20px; box-shadow:0 2px 12px #5473E84D; display:block;'>
                                <h2 style="margin: 0; color: #5473E8; font-family: 'Geist', Arial, sans-serif; font-size: 2rem;">Bem-vindo(a) ao GO Robot!</h2>
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding-bottom: 12px;">
                                <p style="font-size: 1.1rem; margin: 0 0 12px 0; color: #1F2937;">Sua jornada de automação inteligente começa aqui 🤖</p>
                                <p style="font-size: 1rem; margin: 0 0 24px 0; color: #6B7280;">Clique no botão abaixo para validar seu e-mail e liberar seu acesso.</p>
                                <a href="{verification_link}" style="display:inline-block; background: #5473E8; color: #fff; text-decoration: none; font-weight: 600; padding: 14px 32px; border-radius: 12px; font-size: 1.1rem; box-shadow: 0 2px 8px #5473E84D; transition: background 0.2s;">Validar meu e-mail</a>
                                <p style="font-size: 0.95rem; color: #6B7280; margin: 24px 0 0 0;">Se não foi você que criou esta conta, apenas ignore este e-mail.</p>
                                <p style="font-size: 0.85rem; color: #A0AEC0; margin: 16px 0 0 0;">Este link expira em {settings.EMAIL_VERIFICATION_TOKEN_EXPIRATION_HOURS} horas.</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
</html>
"""
        try:
            send_email(to=user.email, subject="Verify your email address - Clinica Go", body=email_body)
            logger.info("[INFO] Verification email sent to %s", user.email)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("[ERROR] Failed to send verification email to %s: %s", user.email, e)

        return UserOut.model_validate(user)

    def authenticate_user(
        self,
        email: str,
        password: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
        remember_me: bool = False,
    ) -> Token | None:
        """Validates credentials and returns tokens with user data.

        Blocks login if email is not verified.
        If MFA is enabled, returns temporary tokens with mfa_required=True.
        If MFA is disabled, returns final tokens with mfa_required=False.

        Args:
            email: User email
            password: User password
            user_agent: Device user-agent (optional)
            ip_address: Client IP address (optional)

        Returns:
            Token with mfa_required=True if MFA enabled (temporary tokens)
            Token with mfa_required=False if MFA disabled (final tokens)
            None if credentials invalid or user inactive
        """
        user = self.repo.get_by_email(email)
        if not user:
            logger.warning("[WARNING] Login failed: user not found for email %s", email)
            return None
        if not user.is_active:
            logger.warning("[WARNING] Login failed: user %s is inactive", email)
            return None

        if not self.email_verification_svc.is_email_verified(user.id):
            logger.warning("[WARNING] Login failed: email not verified for user %s", email)
            raise AuthException("Email not verified. Please check your email for verification link.")
        # Verify password via CredentialService
        if not self.credential_svc.verify_password(user.id, password):
            logger.warning("[WARNING] Login failed: invalid password for user %s", email)
            try:
                self.audit_svc.log_action(
                    action="login_failure",
                    entity_type="User",
                    entity_id="unknown",
                    user_id=None,
                    old_value={"email": email},
                )
            except SQLAlchemyError:
                logger.warning("[WARNING] Audit log failed for login_failure")
            return None

        # pylint: disable=import-outside-toplevel
        # Justification: Avoid circular import dependency between repositories
        from robbot.infra.persistence.repositories.credential_repository import CredentialRepository

        credential_repo = CredentialRepository(self.repo.db)
        credential = credential_repo.get_by_user_id(user.id)
        mfa_enabled = credential.mfa_enabled if credential else False

        if mfa_enabled:
            # Return temporary tokens that require MFA verification
            logger.info("[INFO] Login successful (MFA required): user %s (id=%s)", email, user.id)
            # Create temporary tokens with short expiration (5 minutes)
            temporary_tokens = security.create_token_for_subject(str(user.id), minutes=5, token_type="mfa-pending")
            # Don't create session yet - will be created after MFA verification
            return Token(
                access_token=temporary_tokens,
                refresh_token="",  # No refresh token until MFA verified
                mfa_required=True,
                user=user,
            )

        # Normal login flow (MFA disabled)
        logger.info("Login successful: user %s (id=%s)", email, user.id)
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
        # Set refresh token expiry based on remember_me
        refresh_expiry = None
        if remember_me:
            # 30 days for rememberMe, else default (7 days)
            refresh_expiry = 60 * 24 * 30  # 30 days in minutes
        tokens = security.create_access_refresh_tokens(str(user.id), refresh_expiry)
        # Create session linked to refresh JTI
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
        """Refresh token rotation: validates, revokes the used token and returns a new pair.

        Args:
            refresh_token: Refresh token to be renewed
            user_agent: Device user-agent (optional)
            ip_address: Client IP address (optional)

        Returns:
            New token pair (access + refresh)

        Raises:
            AuthException: If token invalid, revoked, or expired
        """
        # Prevent refresh token reuse (rotation)
        if self.token_repo.is_revoked(refresh_token):
            raise AuthException("Token revoked")
        payload = security.decode_token(refresh_token, verify_exp=True)
        if payload.get("type") != "refresh":
            raise AuthException("Invalid token type")
        subject = payload.get("sub")
        # Validate session via JTI
        jti = payload.get("jti")
        sess = self.session_repo.get_by_jti(jti)
        if not sess or sess.is_revoked or sess.is_expired:
            raise AuthException("Session invalid or revoked")

        # Check idle timeout (30 days of inactivity)
        idle_timeout_days = 30
        last_used = sess.last_used_at or sess.created_at
        # Normalize timezone to avoid naive/aware datetime subtraction errors
        if last_used.tzinfo is None:
            last_used = last_used.replace(tzinfo=UTC)
        idle_duration = datetime.now(UTC) - last_used
        if idle_duration > timedelta(days=idle_timeout_days):
            # Revoke session due to inactivity
            self.session_repo.revoke(sess.id)
            raise AuthException(
                f"Session expired due to inactivity (no activity for {idle_timeout_days} days). "
                "Please login again to create a new session."
            )

        # Update session metadata (last_used + device info if provided)
        device_name = security.parse_device_name(user_agent) if user_agent else None
        self.session_repo.update_last_used(
            sess,
            user_agent=user_agent,
            ip_address=ip_address,
            device_name=device_name,
        )
        # Revoke the used refresh token
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
        logger.info("Token revoked successfully")

    def logout(
        self,
        user_id: int,
        access_token: str | None = None,
        refresh_token: str | None = None,
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
        Generates a short-lived password reset token and sends a beautiful, UX-first email in Portuguese with a button and clear instructions.
        """
        user = self.repo.get_by_email(email)
        if not user:
            return
        token = security.create_token_for_subject(str(user.id), minutes=15, token_type="pw-reset")
        # Password reset link for Go Robot frontend
        frontend_url = "http://localhost:3000/reset?token=" + token
        email_body = f"""
<html>
    <body style=\"background: #FAFAFA; font-family: 'Geist', 'Lora', Arial, sans-serif; color: #1F2937; margin:0; padding:0;\">
        <table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" style=\"background: #FAFAFA; padding: 32px 0;\">
            <tr>
                <td align=\"center\">
                    <table width=\"420\" cellpadding=\"0\" cellspacing=\"0\" style=\"background: #fff; border-radius: 18px; box-shadow: 0 4px 32px 0 #5473E81A; padding: 32px; border: 1px solid #E5E7EB;\">
                        <tr>
                            <td align=\"center\" style=\"padding-bottom: 16px;\">
                                <img src='http://localhost:3000/assets/go_robot.png' alt='GO Robot' width='64' height='64' style='border-radius:12px; margin-bottom:8px;'>
                                <h2 style=\"margin: 0; color: #5473E8; font-family: 'Geist', Arial, sans-serif; font-size: 2rem;\">Recuperação de senha</h2>
                            </td>
                        </tr>
                        <tr>
                            <td align=\"center\" style=\"padding-bottom: 12px;\">
                                <p style=\"font-size: 1.1rem; margin: 0 0 12px 0; color: #1F2937;\">Olá! Recebemos uma solicitação para redefinir a senha da sua conta.</p>
                                <p style=\"font-size: 1rem; margin: 0 0 24px 0; color: #6B7280;\">Para criar uma nova senha, clique no botão abaixo:</p>
                                <a href=\"{frontend_url}\" style=\"display:inline-block; background: #5473E8; color: #fff; text-decoration: none; font-weight: 600; padding: 14px 32px; border-radius: 12px; font-size: 1.1rem; box-shadow: 0 2px 8px #5473E84D; transition: background 0.2s;\">Redefinir senha</a>
                                <p style=\"font-size: 0.95rem; color: #6B7280; margin: 24px 0 0 0;\">Se você não solicitou essa alteração, pode ignorar este e-mail com segurança.</p>
                                <p style=\"font-size: 0.85rem; color: #A0AEC0; margin: 16px 0 0 0;\">Este link expira em 15 minutos por segurança.</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
</html>
"""
        send_email(to=email, subject="Recuperação de senha - GO Robot", body=email_body)

    def reset_password(self, token: str, new_password: str) -> None:
        """Resets password if token is valid and password meets policy.

        Args:
            token: Password reset token
            new_password: New user password

        Raises:
            AuthException: If token invalid or password doesn't meet policy
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
        # Update via service
        self.credential_svc.set_password(user.id, new_password)
        # Revoke all active sessions after password change
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
        """Completes login after MFA verification.

        Args:
            temporary_token: Temporary token from initial login
            code: TOTP code or backup code
            user_agent: User-agent for session tracking (optional)
            ip_address: IP address for session tracking (optional)

        Returns:
            Token with final access and refresh tokens

        Raises:
            AuthException: If token invalid, expired, or MFA verification fails
        """
        # Validate temporary token
        try:
            payload = security.decode_token(temporary_token, verify_exp=True)
        except AuthException as e:
            logger.warning("MFA login failed: invalid temporary token - %s", e)
            raise AuthException("Invalid or expired temporary token") from e

        if payload.get("type") != "mfa-pending":
            raise AuthException("Invalid token type for MFA verification")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthException("Invalid token")

        user = self.repo.get_by_id(int(user_id))
        if not user:
            raise AuthException("User not found")

        # Verify MFA code
        # Try TOTP first, then backup code
        verified = self.mfa_service.verify_mfa(user.id, code)
        if not verified:
            verified = self.mfa_service.verify_backup_code(user.id, code)

        if not verified:
            logger.warning("MFA verification failed for user %s", user.email)
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
        logger.info("MFA verification successful: user %s (id=%s)", user.email, user.id)
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

