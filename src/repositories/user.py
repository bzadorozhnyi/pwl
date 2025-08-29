import uuid
from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.db import get_session
from models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_identifier(
        self, identifier: str, allow_username: bool = True
    ) -> User | None:
        if allow_username:
            statement = select(User).where(
                (User.email == identifier) | (User.username == identifier)
            )
        else:
            statement = select(User).where(User.email == identifier)

        return await self.session.scalar(statement)

    async def get_by_id(self, id: uuid.UUID) -> User | None:
        statement = select(User).where(User.id == id)

        return await self.session.scalar(statement)

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def update(self, user: User) -> User:
        user.updated_at = datetime.now()

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return UserRepository(session)
