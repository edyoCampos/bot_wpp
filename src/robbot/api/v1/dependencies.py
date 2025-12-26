"""Dependências FastAPI para autenticação, autorização e sessões de banco de dados.

Inicializa rate limiter e fornece injeção de dependências para controllers.
"""

from typing import Callable, Generator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from robbot.adapters.repositories.user_repository import UserRepository
from robbot.core import security
from robbot.core.exceptions import AuthException
from robbot.core.rate_limiting import init_rate_limiter
from robbot.infra.db.base import SessionLocal
from robbot.infra.db.models.user_model import UserModel
from robbot.infra.redis.client import get_redis_client

# OAuth2 scheme for documentation (tokens now in cookies, not Authorization header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)

# Flag to ensure rate limiter is initialized only once
_rate_limiter_initialized = False


def initialize_rate_limiter() -> None:
    """Initialize rate limiter with Redis client.
    
    This should be called during application startup.
    """
    global _rate_limiter_initialized
    if not _rate_limiter_initialized:
        redis_client = get_redis_client()
        init_rate_limiter(redis_client)
        _rate_limiter_initialized = True


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Validates token from HttpOnly cookie and returns current user from DB.
    
    Reads access_token from cookie instead of Authorization header.
    """
    # Read access token from HttpOnly cookie
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - access token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = security.decode_token(token)
    except AuthException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token - missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    repo = UserRepository(db)
    user = repo.get_by_id(int(user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def require_role(*allowed_roles: str) -> Callable:
    """
    Dependency factory that checks if current user has one of the allowed roles.
    Raises 403 Forbidden if role check fails.

    Usage: current_admin = Depends(require_role("admin"))
    """

    def role_checker(current_user: UserModel = Depends(get_current_user)) -> UserModel:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker
