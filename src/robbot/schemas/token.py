from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
