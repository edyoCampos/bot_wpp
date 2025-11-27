"""Authentication routes for the public API."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_db, get_current_user
from robbot.schemas.user import UserCreate, UserOut
from robbot.schemas.token import Token, TokenData
from robbot.services.auth_services import AuthService

router = APIRouter()


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user. Controller only maps request -> service -> response.
    """
    service = AuthService(db)
    try:
        user = service.signup(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return user


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate and return access and refresh tokens.
    """
    service = AuthService(db)
    token = service.authenticate_user(
        form_data.username,
        form_data.password,
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
        )
    return token


@router.post("/refresh", response_model=Token)
def refresh_token(payload: TokenData, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    """
    service = AuthService(db)
    try:
        return service.refresh(payload.refresh_token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: TokenData,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Logout that revokes both access and refresh tokens (persisted in DB).
    """
    service = AuthService(db)
    # Revoke refresh token
    if payload.refresh_token:
        service.revoke_token(payload.refresh_token)
    # Revoke access token if provided
    if payload.access_token:
        service.revoke_token(payload.access_token)
    return {}


@router.get("/me", response_model=UserOut)
def read_me(current_user=Depends(get_current_user)):
    """
    Get current authenticated user.
    """
    return current_user


@router.post("/password-recovery", status_code=status.HTTP_202_ACCEPTED)
def password_recovery(email: str, db: Session = Depends(get_db)):
    """
    Initiates password recovery flow (sends email with token).
    """
    service = AuthService(db)
    service.send_password_recovery(email)
    return {"detail": "If the email exists a recovery message was sent"}


@router.post("/password-reset", status_code=status.HTTP_200_OK)
def password_reset(token: str, new_password: str, db: Session = Depends(get_db)):
    """
    Resets password using recovery token.
    """
    service = AuthService(db)
    try:
        service.reset_password(token, new_password)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return {"detail": "Password updated"}
