"""Dependências FastAPI para autenticação, autorização e sessões de banco de dados.

Inicializa rate limiter e fornece injeção de dependências para controllers.
"""

from collections.abc import Callable, Generator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.user_repository import UserRepository
from robbot.core import security
from robbot.core.custom_exceptions import AuthException
from robbot.core.rate_limiting import init_rate_limiter
from robbot.infra.persistence.models.user_model import UserModel
from robbot.infra.db.session import get_db as session_get_db
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
    """Dependency that provides a SQLAlchemy session.

    Delegates to infra.db.session.get_db() for consistency.
    Auto-commits on success, rollbacks on exception.

    Yields:
        SQLAlchemy Session with automatic transaction management
    """
    yield from session_get_db()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> UserModel:
    """
    Validates token from HttpOnly cookie and returns current user from DB.

    Reads access_token from cookie instead of Authorization header.
    """
    # Read access token from HttpOnly cookie
    token = request.cookies.get("access_token")

    # Fallback to Authorization header if cookie is missing (useful for testing/dev)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

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

    # CRITICAL: Check if token was revoked (logout/password change)
    from robbot.infra.persistence.repositories.token_repository import TokenRepository

    token_repo = TokenRepository(db)
    if token_repo.is_revoked(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

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


# ===== DI Container Dependencies =====


def get_container_dep():
    """Dependency to get DI container instance."""
    from robbot.config.container import get_container

    return get_container()


# Backward-compatible wrappers expected by tests (legacy naming)
def get_llm_provider(container=Depends(get_container_dep)):
    return container.get_llm()


def get_vector_store(container=Depends(get_container_dep)):
    return container.get_vector_store()


def get_waha_client(container=Depends(get_container_dep)):
    return container.get_waha()


def get_prompt_loader(container=Depends(get_container_dep)):
    return container.get_prompt_loader()


def get_redis_from_container(container=Depends(get_container_dep)):
    """Dependency to get Redis client from DI container."""
    return container.get_redis()


def get_llm_from_container(container=Depends(get_container_dep)):
    """Dependency to get LLM provider from DI container."""
    return container.get_llm()  # type: LLMProvider


def get_vector_store_from_container(container=Depends(get_container_dep)):
    """Dependency to get vector store from DI container."""
    return container.get_vector_store()  # type: VectorStore


def get_waha_from_container(container=Depends(get_container_dep)):
    """Dependency to get WAHA WhatsApp client from DI container."""
    return container.get_waha()  # type: WAHAClientInterface


def get_prompt_loader_from_container(container=Depends(get_container_dep)):
    """Dependency to get prompt loader from DI container."""
    return container.get_prompt_loader()  # type: PromptLoader

