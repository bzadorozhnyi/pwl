from pydantic import BaseModel


class TokenPairOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshIn(BaseModel):
    refresh_token: str


class TokenAccessOut(BaseModel):
    access_token: str
