from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import bcrypt
import jwt

from robbot.config.settings import settings
from robbot.core.custom_exceptions import AuthException


def parse_device_name(user_agent: str | None) -> str:
    """
    Parse user agent string to extract a human-readable device name.

    Examples:
    - "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0"
      → "Chrome on Windows"
    - "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1"
      → "Safari on iPhone"
    - "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0"
      → "Chrome on macOS"
    """
    if not user_agent:
        return "Unknown Device"

    ua = user_agent.lower()

    # Detect browser
    browser = "Unknown Browser"
    if "edg/" in ua or "edge/" in ua:
        browser = "Edge"
    elif "chrome/" in ua and "edg/" not in ua:
        browser = "Chrome"
    elif "firefox/" in ua:
        browser = "Firefox"
    elif "safari/" in ua and "chrome/" not in ua:
        browser = "Safari"
    elif "opera/" in ua or "opr/" in ua:
        browser = "Opera"

    # Detect OS/Device
    os_name = "Unknown OS"
    if "iphone" in ua:
        os_name = "iPhone"
    elif "ipad" in ua:
        os_name = "iPad"
    elif "android" in ua:
        os_name = "Android"
    elif "windows nt" in ua:
        os_name = "Windows"
    elif "mac os x" in ua:
        os_name = "macOS"
    elif "linux" in ua:
        os_name = "Linux"

    return f"{browser} on {os_name}"


def get_password_hash(password: str) -> str:
    """Return a bcrypt hash for the plain password.

    Truncates password to 72 UTF-8 bytes to respect bcrypt limitation.
    """
    # Bcrypt has a hard limit of 72 bytes
    password_bytes = password.encode("utf-8")

    # Truncate if necessary (preserving UTF-8 validity)
    if len(password_bytes) > 72:
        # Decode with error handling to avoid cutting in the middle of a character
        password_bytes = password_bytes[:72]
        password = password_bytes.decode("utf-8", errors="ignore")
        password_bytes = password.encode("utf-8")

    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string (bcrypt returns bytes)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against the hashed value."""
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_token_for_subject(subject: str, minutes: int, token_type: str, jti: str | None = None) -> str:
    """
    Generic token generator used for refresh, access and other short-lived tokens.
    """
    expire = datetime.now(UTC) + timedelta(minutes=minutes)
    to_encode: dict[str, Any] = {
        "exp": expire,
        "iat": datetime.now(UTC),
        "sub": str(subject),
        "type": token_type,
    }
    if token_type == "refresh":
        # incluir JTI para controle de sessão
        to_encode["jti"] = jti or uuid4().hex
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_refresh_tokens(subject: str, refresh_expiry_minutes: int | None = None) -> dict[str, str]:
    """
    Create access and refresh tokens for subject.
    Optionally override refresh token expiry.
    """
    access_token = create_token_for_subject(subject, minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES, token_type="access")
    refresh_minutes = (
        refresh_expiry_minutes if refresh_expiry_minutes is not None else settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    refresh_token = create_token_for_subject(
        subject,
        minutes=refresh_minutes,
        token_type="refresh",
        jti=uuid4().hex,
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


def decode_token(token: str, verify_exp: bool = True) -> dict[str, Any]:
    """
    Decode and verify JWT token. Raises AuthException on failures.
    """
    options = {"verify_exp": verify_exp}
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options=options)
    except jwt.ExpiredSignatureError as exc:
        raise AuthException("Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthException("Invalid token") from exc


def validate_password_policy(password: str) -> None:
    """
    Apply minimal password policy: length >= 8
    """
    if not password or len(password) < 8:
        raise AuthException("Password must be at least 8 characters")
