"""Authentication schema definitions for API requests and responses.

This module contains ALL authentication-related DTOs, completely separated from user profile schemas.
This separation follows the principle of separating security concerns from domain concerns.

Author: Sistema de Auditoria de Segurança
Date: 2025-12-23
Phase: FASE 0 - Preparação
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ============================================================================
# REGISTRATION & LOGIN
# ============================================================================


class SignupRequest(BaseModel):
    """Schema for user registration (signup) requests.

    This replaces UserCreate for authentication purposes.
    Separates credential creation from user profile creation.
    """

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str | None = None
    role: Literal["admin", "user"] = "user"

    @field_validator("password")
    @classmethod
    def password_policy(cls, v: str) -> str:
        """Enforce password complexity rules.

        Requirements:
        - Minimum 8 characters
        - Maximum 128 characters (to prevent DoS via bcrypt)
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must not exceed 128 characters")
        return v


class LoginRequest(BaseModel):
    """Schema for login requests."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema for successful login response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes in seconds
    mfa_required: bool = False  # For future MFA support


class LogoutRequest(BaseModel):
    """Schema for logout requests."""

    refresh_token: str


# ============================================================================
# TOKEN REFRESH
# ============================================================================


class RefreshRequest(BaseModel):
    """Schema for token refresh requests."""

    refresh_token: str


class RefreshResponse(BaseModel):
    """Schema for token refresh response.

    Includes new access + refresh tokens (rotation).
    """

    access_token: str
    refresh_token: str  # New token due to rotation
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes


# ============================================================================
# PASSWORD MANAGEMENT
# ============================================================================


class ForgotPasswordRequest(BaseModel):
    """Schema for password recovery initiation."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Schema for password reset with token."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_policy(cls, v: str) -> str:
        """Enforce password complexity rules."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must not exceed 128 characters")
        return v


class ChangePasswordRequest(BaseModel):
    """Schema for authenticated password change."""

    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_policy(cls, v: str) -> str:
        """Enforce password complexity rules."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must not exceed 128 characters")
        return v


# ============================================================================
# EMAIL VERIFICATION
# ============================================================================


class VerifyEmailRequest(BaseModel):
    """Schema for email verification."""

    token: str


class ResendEmailRequest(BaseModel):
    """Schema for resending email verification."""

    email: EmailStr


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================


class SessionResponse(BaseModel):
    """Schema for session information."""

    id: int
    user_id: int
    device_name: str | None = None
    ip_address: str
    user_agent: str | None = None
    created_at: datetime
    last_used_at: datetime
    expires_at: datetime
    is_current: bool = False  # True if this is the requesting session

    model_config = ConfigDict(from_attributes=True)


class SessionListResponse(BaseModel):
    """Schema for listing user sessions."""

    sessions: list[SessionResponse]
    total: int


class RevokeSessionRequest(BaseModel):
    """Schema for revoking a specific session."""

    session_id: int


# ============================================================================
# AUTH SESSION INFO (GET /auth/me)
# ============================================================================


class AuthSessionResponse(BaseModel):
    """Schema for current authentication session information.

    This is returned by GET /auth/me and contains ONLY auth-related data.
    For user profile data, use GET /users/me instead.
    """

    user_id: int
    email: EmailStr
    role: str
    is_active: bool
    email_verified: bool = False  # Future: email verification
    mfa_enabled: bool = False  # Future: MFA support
    session_id: int | None = None
    last_login_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ADMIN - USER BLOCKING
# ============================================================================


class BlockUserRequest(BaseModel):
    """Schema for blocking a user (admin only)."""

    reason: str | None = None


class UnblockUserRequest(BaseModel):
    """Schema for unblocking a user (admin only)."""

    reason: str | None = None


# ============================================================================
# MFA (Multi-Factor Authentication) - PHASE 5
# ============================================================================


class MfaSetupResponse(BaseModel):
    """Schema for MFA setup response."""

    secret: str
    qr_code: str  # Base64 encoded QR code image
    backup_codes: list[str]


class MfaVerifyRequest(BaseModel):
    """Schema for MFA verification."""

    code: str = Field(..., min_length=6, max_length=6)


class MfaDisableRequest(BaseModel):
    """Schema for disabling MFA."""

    password: str
    code: str = Field(..., min_length=6, max_length=6)


class BackupCodesResponse(BaseModel):
    """Schema for backup codes generation."""

    codes: list[str]


# ============================================================================
# AUDIT & SECURITY
# ============================================================================


class AuditLogEntry(BaseModel):
    """Schema for audit log entries."""

    id: int
    user_id: int | None = None
    action: str
    ip_address: str | None = None
    user_agent: str | None = None
    metadata: dict | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    """Schema for listing audit logs."""

    logs: list[AuditLogEntry]
    total: int
