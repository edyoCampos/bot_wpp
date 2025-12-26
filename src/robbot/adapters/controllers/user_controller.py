"""User management controller for CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_db, get_current_user, require_role
from robbot.core.exceptions import NotFoundException
from robbot.schemas.user import MessageResponse, UserList, UserOut, UserUpdate
from robbot.schemas.auth import BlockUserRequest, UnblockUserRequest
from robbot.services.user_service import UserService

router = APIRouter()


@router.get("/users/me", response_model=UserOut)
def get_current_user_profile(
    current_user=Depends(get_current_user),
):
    """Obtém perfil do usuário autenticado atual.
    
    Retorna dados de perfil do usuário (nome, email, role).
    Para informações de sessão de autenticação, use GET /auth/me.
    """
    return current_user


@router.patch("/users/me", response_model=UserOut)
def update_current_user_profile(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Atualiza perfil do usuário autenticado atual.
    
    Permite usuários atualizarem seus próprios campos de perfil (ex: full_name).
    Não pode atualizar email, password, is_active ou role - use endpoints dedicados.
    """
    service = UserService(db)
    try:
        return service.update_user(current_user.id, payload)
    except NotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/users", response_model=UserList)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_admin=Depends(require_role("admin")),
):
    """Retrieve paginated list of users (admin only)."""
    service = UserService(db)
    users, total = service.list_users(skip=skip, limit=limit)
    return UserList(users=users, total=total, skip=skip, limit=limit)


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_role("admin")),
):
    """Retrieve a single user by ID (admin only)."""
    service = UserService(db)
    try:
        return service.get_user(user_id)
    except NotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_role("admin")),
):
    """Update user profile fields (admin only)."""
    service = UserService(db)
    try:
        return service.update_user(user_id, payload)
    except NotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/users/{user_id}", response_model=MessageResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_role("admin")),
):
    """Deactivate user (admin only)."""
    service = UserService(db)
    try:
        service.deactivate_user(user_id)
        return MessageResponse(detail=f"User {user_id} deactivated successfully")
    except NotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/users/{user_id}/block", response_model=UserOut)
def block_user(
    user_id: int,
    payload: BlockUserRequest | None = None,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_role("admin")),
):
    """Block user (admin only): sets is_active=False, revokes sessions, audits."""
    service = UserService(db)
    try:
        return service.block_user(user_id, reason=(payload.reason if payload else None))
    except NotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/users/{user_id}/unblock", response_model=UserOut)
def unblock_user(
    user_id: int,
    payload: UnblockUserRequest | None = None,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_role("admin")),
):
    """Unblock user (admin only): sets is_active=True and audits."""
    service = UserService(db)
    try:
        return service.unblock_user(user_id, reason=(payload.reason if payload else None))
    except NotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
