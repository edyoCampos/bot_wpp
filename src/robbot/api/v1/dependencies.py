"""FastAPI dependencies for authentication, authorization and database sessions."""

from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from robbot.adapters.repositories.user_repository import UserRepository
from robbot.core import security
from robbot.core.exceptions import AuthException
from robbot.infra.db.base import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


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
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Validates token and returns current user from DB.
    """
    try:
        payload = security.decode_token(token)
    except AuthException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    repo = UserRepository(db)
    user = repo.get_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive"
        )
    return user


def require_role(*allowed_roles: str):
    """
    Dependency factory that checks if current user has one of the allowed roles.
    Raises 403 Forbidden if role check fails.

    Usage: current_admin = Depends(require_role("admin"))
    """

    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker
