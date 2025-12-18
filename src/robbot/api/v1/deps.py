"""
FastAPI dependencies para controllers.

Dependencies para autenticação e acesso a recursos.
"""

from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import redis

from robbot.adapters.repositories.user_repository import UserRepository
from robbot.core import security
from robbot.core.exceptions import AuthException
from robbot.infra.db.session import get_db
from robbot.infra.redis.client import get_redis_client
from robbot.infra.db.models.user_model import UserModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency que fornece uma sessão do SQLAlchemy.
    """
    yield from get_db()


def get_redis() -> redis.Redis:
    """
    Dependency que retorna cliente Redis.
    """
    return get_redis_client()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_session)
) -> UserModel:
    """
    Valida token JWT e retorna usuário atual do banco.
    
    Raises:
        HTTPException 401: Token inválido ou usuário não encontrado
        HTTPException 403: Usuário inativo
    """
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
            detail="Invalid token payload"
        )
    
    # UserRepository
    repo = UserRepository(db)
    user = repo.get_by_id(int(user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user
