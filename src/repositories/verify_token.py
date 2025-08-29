import uuid
from datetime import datetime
from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.db import get_session
from models.verify_token import VerifyToken


class VerifyTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, token: VerifyToken):
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)

        return token

    async def update(self, token: VerifyToken):
        token.created_at = datetime.now()

        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)

        return token

    async def get_by_email(self, email: str) -> VerifyToken | None:
        statement = select(VerifyToken).where(VerifyToken.email == email)

        return await self.session.scalar(statement)

    async def get_by_id(self, id: uuid.UUID) -> VerifyToken | None:
        statement = select(VerifyToken).where(VerifyToken.id == id)

        return await self.session.scalar(statement)

    async def get_by_token(self, token: uuid.UUID) -> VerifyToken | None:
        statement = select(VerifyToken).where(VerifyToken.token == token)

        return await self.session.scalar(statement)

    async def delete(self, id: uuid.UUID):
        token = await self.get_by_id(id)
        if token:
            await self.session.delete(token)
            await self.session.commit()


def get_verify_token_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> VerifyTokenRepository:
    return VerifyTokenRepository(session)
