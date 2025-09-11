from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from core.db import get_session
from core.jwt import AuthJWTService, get_auth_jwt_service
from core.logging import logger
from exceptions import (
    AuthorizationException,
    ForbiddenException,
    InputException,
    NotFoundException,
)
from models.family import Family, FamilyMember, FamilyRole
from models.shopping_list import ShoppingList
from models.user import User
from repositories.family import FamilyRepository, get_family_repository
from repositories.shopping_list import (
    ShoppingListRepository,
    get_shopping_list_repository,
)
from repositories.user import UserRepository, get_user_repository
from schemas.user import (
    FamilyInfo,
    UserAuthCredentialsIn,
    UserIn,
    UserOut,
    UserProfileOut,
    UserWithTokensOut,
)


class UserService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        family_repository: FamilyRepository,
        shopping_list_repository: ShoppingListRepository,
        auth_jwt_service: AuthJWTService,
    ):
        self.session = session
        self.user_repository = user_repository
        self.family_repository = family_repository
        self.shopping_list_repository = shopping_list_repository
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

            family = await self.family_repository.create()
            _family_member = await self.family_repository.add_member(
                family_id=family.id, user_id=user.id, role=FamilyRole.ADMIN
            )

            _default_shopping_list = await self.shopping_list_repository.create(
                ShoppingList(
                    creator_id=user.id, family_id=family.id, name="Family Shopping List"
                )
            )

        return user, family

    async def login(self, user_credentials: UserAuthCredentialsIn) -> UserWithTokensOut:
        logger.info("start user login")
        user = await self.authenticate_user(user_credentials)
        if not user:
            raise AuthorizationException("Invalid identifier or password")

        tokens = self.auth_jwt_service.create_token_pair({"sub": str(user.id)})

        return UserWithTokensOut(user=UserOut.model_validate(user), tokens=tokens)

    async def login_admin(
        self, user_credentials: UserAuthCredentialsIn
    ) -> UserWithTokensOut:
        logger.info("start admin login")
        user = await self.authenticate_user(user_credentials)
        if not user:
            raise AuthorizationException("Invalid identifier or password")

        if user.is_admin is False:
            raise ForbiddenException("User is not admin")

        tokens = self.auth_jwt_service.create_token_pair({"sub": str(user.id)})

        return UserWithTokensOut(user=UserOut.model_validate(user), tokens=tokens)

    async def authenticate_user(
        self, user_credentials: UserAuthCredentialsIn
    ) -> User | None:
        user = await self.user_repository.get_by_identifier(user_credentials.identifier)
        if not user:
            logger.warning("user not found")
            return None

        if not self.auth_jwt_service.verify_password(
            user_credentials.password, user.password
        ):
            logger.warning("invalid password")
            return None

        return user

    async def get_user_from_token(self, token: str) -> User:
        credentials_exception = AuthorizationException(
            "Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}
        )

        try:
            payload = self.auth_jwt_service.decode_token(token)
        except Exception:
            raise credentials_exception
        user_id = payload.get("sub")
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise credentials_exception

        return user

    async def get_profile(self, user: User) -> UserProfileOut:
        statement = (
            select(User)
            .options(selectinload(User.families).selectinload(FamilyMember.family))
            .where(User.id == user.id)
        )

        result = await self.session.execute(statement)
        row = result.first()

        if not row:
            raise NotFoundException("User profile not found.")

        families = [
            FamilyInfo(id=member.family.id, role=member.role)
            for member in user.families
        ]

        if len(families) == 0:
            logger.warning("user has no families")
            raise NotFoundException("User profile not found.")

        return UserProfileOut(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            families=families,
        )


def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    family_repository: Annotated[FamilyRepository, Depends(get_family_repository)],
    shopping_list_repository: Annotated[
        ShoppingListRepository, Depends(get_shopping_list_repository)
    ],
    auth_jwt_service: Annotated[AuthJWTService, Depends(get_auth_jwt_service)],
) -> UserService:
    return UserService(
        session,
        user_repository,
        family_repository,
        shopping_list_repository,
        auth_jwt_service,
    )
