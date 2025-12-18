"""
FastAPI dependencies para controllers async.

Versão async das dependencies para compatibilidade com controllers modernos.
"""

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from robbot.adapters.repositories.user_repository import UserRepository
from robbot.core import security
from robbot.core.exceptions import AuthException
from robbot.infra.db.session import async_session_maker
from robbot.infra.redis_client import get_redis
from robbot.domain.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency que fornece uma sessão async do SQLAlchemy.
    """
    async with async_session_maker() as session:
        yield session


async def get_redis_client() -> Redis:
    """
    Dependency que retorna cliente Redis async.
    """
    return get_redis()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session)
) -> User:
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
    
    # UserRepository async
    repo = UserRepository(db)
    user = await repo.get_by_id(int(user_id))
    
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
