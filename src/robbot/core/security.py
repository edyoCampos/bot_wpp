from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, Dict
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from robbot.config.settings import settings
from robbot.core.exceptions import AuthException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_scheme = HTTPBearer()


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
    """Return a bcrypt hash for the plain password."""
    # Truncate to 72 bytes to avoid bcrypt limitation
    password_bytes = password.encode('utf-8')[:72]
    return pwd_context.hash(password_bytes.decode('utf-8'))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against the hashed value."""
    return pwd_context.verify(plain_password, hashed_password)


def create_token_for_subject(subject: str, minutes: int, token_type: str, jti: str | None = None) -> str:
    """
    Generic token generator used for refresh, access and other short-lived tokens.
    """
    expire = datetime.now(UTC) + timedelta(minutes=minutes)
    to_encode: Dict[str, Any] = {
        "exp": expire,
        "iat": datetime.now(UTC),
        "sub": str(subject),
        "type": token_type,
    }
    if token_type == "refresh":
        # incluir JTI para controle de sessão
        to_encode["jti"] = jti or uuid4().hex
    token = jwt.encode(to_encode, settings.SECRET_KEY,
                       algorithm=settings.ALGORITHM)
    return token


def create_access_refresh_tokens(subject: str) -> Dict[str, str]:
    """
    Create access and refresh tokens for subject.
    """
    access_token = create_token_for_subject(
        subject, minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES, token_type="access"
    )
    refresh_token = create_token_for_subject(
        subject,
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        token_type="refresh",
        jti=uuid4().hex,
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


def decode_token(token: str, verify_exp: bool = True) -> Dict[str, Any]:
    """
    Decode and verify JWT token. Raises AuthException on failures.
    """
    options = {"verify_exp": verify_exp}
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[
                             settings.ALGORITHM], options=options)
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthException("Token expired")
    except jwt.InvalidTokenError:
        raise AuthException("Invalid token")


def validate_password_policy(password: str) -> None:
    """
    Apply minimal password policy: length >= 8
    """
    if not password or len(password) < 8:
        raise AuthException("Password must be at least 8 characters")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    """
    FastAPI dependency to extract and validate the current user from JWT token.
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session (optional, for future user validation)
    
    Returns:
        dict: Decoded token payload with user info
    
    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        payload = decode_token(token, verify_exp=True)
        
        # Validate token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Expected access token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract user_id from subject
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Return user context (can be extended with DB validation)
        return {
            "user_id": int(user_id),
            "exp": payload.get("exp"),
            "iat": payload.get("iat"),
        }
    
    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
