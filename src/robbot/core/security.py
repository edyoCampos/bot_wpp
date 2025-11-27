from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict

import jwt
from passlib.context import CryptContext

from robbot.config.settings import settings
from robbot.core.exceptions import AuthException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Return a bcrypt hash for the plain password."""
    # Truncate to 72 bytes to avoid bcrypt limitation
    password_bytes = password.encode('utf-8')[:72]
    return pwd_context.hash(password_bytes.decode('utf-8'))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against the hashed value."""
    return pwd_context.verify(plain_password, hashed_password)


def create_token_for_subject(subject: str, minutes: int, token_type: str) -> str:
    """
    Generic token generator used for refresh, access and other short-lived tokens.
    """
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    to_encode: Dict[str, Any] = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(subject),
        "type": token_type,
    }
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
        subject, minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES, token_type="refresh"
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
