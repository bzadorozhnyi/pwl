from typing import Annotated

from fastapi import Depends, HTTPException, status

from core.jwt import AuthJWTService, get_auth_jwt_service
from models.user import User
from repositories.user import UserRepository, get_user_repository
from schemas.user import UserIn, UserLoginCredentials, UserOut


class UserService:
    def __init__(
        self, user_repository: UserRepository, auth_jwt_service: AuthJWTService
    ):
        self.user_repository = user_repository
        self.auth_jwt_service = auth_jwt_service

    async def register(self, user_in: UserIn) -> UserOut:
        if await self.user_repository.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = self.auth_jwt_service.get_password_hash(user_in.password)

        user_db = User(
            email=user_in.email,
            full_name=user_in.full_name,
            password=hashed_password,
        )

        result = await self.user_repository.create(user_db)

        return UserOut.model_validate(result)

    async def authenticate_user(
        self, user_credentials: UserLoginCredentials
    ) -> UserOut | None:
        user = await self.user_repository.get_by_email(user_credentials.email)
        if not user:
            return None

        if not self.auth_jwt_service.verify_password(
            user_credentials.password, user.password
        ):
            return None

        return UserOut.model_validate(user)


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    auth_jwt_service: Annotated[AuthJWTService, Depends(get_auth_jwt_service)],
):
    return UserService(user_repository, auth_jwt_service)
