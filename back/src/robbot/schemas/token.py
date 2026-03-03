from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    mfa_required: bool = False
    user: object | None = None  # UserModel object


class TokenData(BaseModel):
    refresh_token: str | None = None
    access_token: str | None = None
