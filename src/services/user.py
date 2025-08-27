from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_session
from core.jwt import AuthJWTService, get_auth_jwt_service
from core.logging import logger
from exceptions import AuthorizationException, InputException
from models.family import Family, FamilyRole
from models.user import User
from repositories.family import FamilyRepository, get_family_repository
from repositories.user import UserRepository, get_user_repository
from schemas.token import TokenPairOut
from schemas.user import (
    UserAuthCredentialsIn,
    UserIn,
    UserOut,
    UserWithTokensOut,
)


class UserService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        family_repository: FamilyRepository,
        auth_jwt_service: AuthJWTService,
    ):
        self.session = session
        self.user_repository = user_repository
        self.family_repository = family_repository
        self.auth_jwt_service = auth_jwt_service

    async def register(self, user_in: UserIn) -> UserWithTokensOut:
        logger.info("start user registration")
        if await self.user_repository.get_by_identifier(
            user_in.email, allow_username=False
        ):
            logger.warning("attempt to register already existing email")
            raise InputException("Email already registered")

        hashed_password = self.auth_jwt_service.get_password_hash(user_in.password)

        user_db = User(
            email=user_in.email,
            username=user_in.email,
            password=hashed_password,
            first_name=user_in.first_name,
            last_name=user_in.last_name,
        )

        user, _ = await self._create_user_and_family(user_db)

        logger.info("user and family successfully created")

        tokens = self.auth_jwt_service.create_token_pair({"sub": str(user.id)})

        return UserWithTokensOut(user=UserOut.model_validate(user), tokens=tokens)

    async def _create_user_and_family(self, user_db: User) -> tuple[User, Family]:
        async with self.session.transaction():
            user = await self.user_repository.create(user_db)
            family = await self.family_repository.create(
                user_id=user.id, role=FamilyRole.ADMIN
            )

        return user, family

    async def login(self, user_credentials: UserAuthCredentialsIn) -> TokenPairOut:
        logger.info("start user login")
        user = await self.authenticate_user(user_credentials)
        if not user:
            raise AuthorizationException("Invalid identifier or password")

        tokens = self.auth_jwt_service.create_token_pair({"sub": str(user.id)})

        return UserWithTokensOut(user=UserOut.model_validate(user), tokens=tokens)

    async def authenticate_user(
        self, user_credentials: UserAuthCredentialsIn
    ) -> UserOut | None:
        user = await self.user_repository.get_by_identifier(user_credentials.identifier)
        if not user:
            logger.warning("user not found")
            return None

        if not self.auth_jwt_service.verify_password(
            user_credentials.password, user.password
        ):
            logger.warning("invalid password")
            return None

        return UserOut.model_validate(user)


def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    family_repository: Annotated[FamilyRepository, Depends(get_family_repository)],
    auth_jwt_service: Annotated[AuthJWTService, Depends(get_auth_jwt_service)],
) -> UserService:
    return UserService(session, user_repository, family_repository, auth_jwt_service)
