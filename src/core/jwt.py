from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from core.config import settings
from schemas.token import TokenPairOut

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthJWTService:
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def _create_token(self, data: dict, expires_delta: timedelta):
        to_encode = data.copy()
        expire = datetime.now(tz=timezone.utc) + expires_delta
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        if not expires_delta:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        return self._create_token(data, expires_delta)

    def create_refresh_token(self, data: dict, expires_delta: timedelta | None = None):
        if not expires_delta:
            expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        return self._create_token(data, expires_delta)

    def create_token_pair(self, data: dict):
        access_token = self.create_access_token(data)
        refresh_token = self.create_refresh_token(data)

        return TokenPairOut(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def decode_refresh_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": False,
                    "verify_iat": False,
                    "verify_aud": False,
                    "verify_iss": False,
                    "verify_sub": False,
                    "verify_jti": False,
                },
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Refresh token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid refresh token")


def get_auth_jwt_service() -> AuthJWTService:
    return AuthJWTService()
