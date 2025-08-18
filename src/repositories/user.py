from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.db import get_session
from models.user import UserDB


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> UserDB | None:
        statement = select(UserDB).where(UserDB.email == email)
        result = await self.session.execute(statement)

        return result.scalars().one_or_none()

    async def create(self, user: UserDB) -> UserDB:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return UserRepository(session)
