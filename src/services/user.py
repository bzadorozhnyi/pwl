from typing import Annotated

from fastapi import Depends

from core.jwt import AuthJWTService, get_auth_jwt_service
from core.logging import logger
from exceptions.auth import EmailAlreadyRegisteredError, InvalidCredentialError
from models.user import User
from repositories.user import UserRepository, get_user_repository
from schemas.token import TokenPairOut
from schemas.user import UserAuthCredentialsIn, UserIn, UserOut


class UserService:
    def __init__(
        self, user_repository: UserRepository, auth_jwt_service: AuthJWTService
    ):
        self.user_repository = user_repository
        self.auth_jwt_service = auth_jwt_service

    async def register(self, user_in: UserIn) -> UserOut:
        logger.info("start user registration")
        if await self.user_repository.get_by_email(user_in.email):
            logger.warning("attempt to register already existing email")
            raise EmailAlreadyRegisteredError()

        hashed_password = self.auth_jwt_service.get_password_hash(user_in.password)

        user_db = User(
            email=user_in.email,
            full_name=user_in.full_name,
            password=hashed_password,
        )

        result = await self.user_repository.create(user_db)
        logger.info("user successfully created")

        return UserOut.model_validate(result)

    async def login(self, user_credentials: UserAuthCredentialsIn) -> TokenPairOut:
        logger.info("start user login")
        user = await self.authenticate_user(user_credentials)
        if not user:
            raise InvalidCredentialError()

        return self.auth_jwt_service.create_token_pair({"sub": user.id})

    async def authenticate_user(
        self, user_credentials: UserAuthCredentialsIn
    ) -> UserOut | None:
        user = await self.user_repository.get_by_email(user_credentials.email)
        if not user:
            logger.warning("email not found")
            return None

        if not self.auth_jwt_service.verify_password(
            user_credentials.password, user.password
        ):
            logger.warning("invalid password")
            return None

        return UserOut.model_validate(user)


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    auth_jwt_service: Annotated[AuthJWTService, Depends(get_auth_jwt_service)],
) -> UserService:
    return UserService(user_repository, auth_jwt_service)
