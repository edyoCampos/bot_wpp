"""Definições de schemas MFA para requests e responses da API.

Implementa autenticação multi-fator via TOTP (Time-based One-Time Password).
"""

from pydantic import BaseModel, Field


class MfaSetupRequest(BaseModel):
    """Request to setup MFA (no payload needed, uses current user)."""
    pass


class MfaSetupResponse(BaseModel):
    """Response after setting up MFA with QR code and backup codes."""
    
    secret: str = Field(..., description="Base32 TOTP secret")
    qr_code_base64: str = Field(..., description="QR code image as base64")
    backup_codes: list[str] = Field(..., description="List of backup codes (plain text)")


class MfaVerifyRequest(BaseModel):
    """Request to verify MFA code."""
    
    code: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP code")


class MfaVerifyResponse(BaseModel):
    """Response after verifying MFA code."""
    
    verified: bool
    message: str


class MfaDisableRequest(BaseModel):
    """Request to disable MFA (requires MFA code for confirmation)."""
    
    code: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP code to confirm")


class MfaDisableResponse(BaseModel):
    """Response after disabling MFA."""
    
    message: str
