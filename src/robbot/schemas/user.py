"""User schema definitions for API requests and responses."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Schema for user registration requests."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str | None = None
    role: str = "user"

    @field_validator("password")
    @classmethod
    def password_policy(cls, v: str) -> str:
        """Enforce minimum password length."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserOut(BaseModel):
    """Schema for user data in API responses."""

    id: int
    email: EmailStr
    full_name: str | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserOut):
    """Internal schema including hashed password for persistence layer."""

    hashed_password: str


class UserUpdate(BaseModel):
    """Schema para atualização de campos de perfil do usuário.
    
    Nota: is_active é gerenciado via endpoints de bloqueio:
    - POST /users/{id}/block
    - POST /users/{id}/unblock
    """

    full_name: str | None = None


class UserList(BaseModel):
    """Schema for paginated user list response."""

    users: list[UserOut]
    total: int
    skip: int
    limit: int


class MessageResponse(BaseModel):
    """Standard message response for operations."""

    detail: str


class ForbiddenResponse(BaseModel):
    """Response schema for 403 Forbidden access errors."""

    detail: str = "Access denied. Insufficient permissions."
