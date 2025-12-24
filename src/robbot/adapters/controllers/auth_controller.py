"""Authentication routes for the public API.

FASE 0: Added rate limiting to prevent brute force attacks.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.config.settings import get_settings
from robbot.core.rate_limiting import (
    RATE_LIMIT_LOGIN,
    RATE_LIMIT_PASSWORD_RECOVERY,
    RATE_LIMIT_PASSWORD_RESET,
    RATE_LIMIT_REFRESH,
    RATE_LIMIT_REGISTER,
)
from robbot.schemas.token import Token, TokenData
from robbot.schemas.user import UserCreate, UserOut
from robbot.services.auth_services import AuthService

router = APIRouter()
settings = get_settings()


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@RATE_LIMIT_REGISTER  # 3 per hour per IP
async def signup(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user. Controller only maps request -> service -> response.
    
    Rate limited: 3 requests per hour per IP address.
    """
    service = AuthService(db)
    try:
        user = service.signup(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return user


@router.post("/token", response_model=dict)
@RATE_LIMIT_LOGIN  # 5 per 15min per IP
async def login_for_access_token(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate and return tokens in HttpOnly cookies + user data.
    
    Returns public user data in response body.
    Stores access_token and refresh_token in HttpOnly cookies.
    
    Rate limited: 5 requests per 15 minutes per IP address.
    """
    service = AuthService(db)
    token_result = service.authenticate_user(
        form_data.username,
        form_data.password,
    )
    if not token_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
        )
    
    # Set refresh token in HttpOnly cookie (strict path for security)
    response.set_cookie(
        key="refresh_token",
        value=token_result.refresh_token,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        path="/api/v1/auth/refresh",  # Only sent to refresh endpoint
        domain=settings.COOKIE_DOMAIN,
    )
    
    # Set access token in HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=token_result.access_token,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/api/v1",  # Sent to all API endpoints
        domain=settings.COOKIE_DOMAIN,
    )
    
    # Return public user data (no tokens in response body)
    return {
        "user": UserOut.model_validate(token_result.user).model_dump(),
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/refresh", response_model=dict)
@RATE_LIMIT_REFRESH  # 10 per 1min per user
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token from HttpOnly cookie.
    
    Rate limited: 10 requests per minute per user.
    """
    # Read refresh token from cookie
    refresh_token_value = request.cookies.get("refresh_token")
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )
    
    service = AuthService(db)
    try:
        token_result = service.refresh(refresh_token_value)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    
    # Update access token in cookie
    response.set_cookie(
        key="access_token",
        value=token_result.access_token,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/api/v1",
        domain=settings.COOKIE_DOMAIN,
    )
    
    # Optional: Implement refresh token rotation for extra security
    if hasattr(token_result, 'new_refresh_token') and token_result.new_refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=token_result.new_refresh_token,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            path="/api/v1/auth/refresh",
            domain=settings.COOKIE_DOMAIN,
        )
    
    return {
        "message": "Token refreshed successfully",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Logout: revoke tokens in DB and clear HttpOnly cookies.
    """
    # Read tokens from cookies
    access_token = request.cookies.get("access_token")
    refresh_token_value = request.cookies.get("refresh_token")
    
    service = AuthService(db)
    
    # Revoke tokens in database
    if refresh_token_value:
        try:
            service.revoke_token(refresh_token_value)
        except Exception:
            pass  # Token might already be invalid/expired
    
    if access_token:
        try:
            service.revoke_token(access_token)
        except Exception:
            pass
    
    # Clear cookies
    response.delete_cookie("access_token", path="/api/v1")
    response.delete_cookie("refresh_token", path="/api/v1/auth/refresh")
    
    return None


@router.get("/me", response_model=UserOut)
def read_me(current_user=Depends(get_current_user)):
    """
    Get current authenticated user.
    """
    return current_user


@router.post("/password-recovery", status_code=status.HTTP_202_ACCEPTED)
@RATE_LIMIT_PASSWORD_RECOVERY  # 3 per hour per email
async def password_recovery(request: Request, email: str, db: Session = Depends(get_db)):
    """
    Initiates password recovery flow (sends email with token).
    
    Rate limited: 3 requests per hour per email address.
    """
    service = AuthService(db)
    service.send_password_recovery(email)
    return {"detail": "If the email exists a recovery message was sent"}


@router.post("/password-reset", status_code=status.HTTP_200_OK)
@RATE_LIMIT_PASSWORD_RESET  # 5 per 15min per IP
async def password_reset(request: Request, token: str, new_password: str, db: Session = Depends(get_db)):
    """
    Resets password using recovery token.
    
    Rate limited: 5 requests per 15 minutes per IP address.
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
