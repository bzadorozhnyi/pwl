import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_session
from models.family import Family, FamilyRole


class FamilyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: uuid.UUID, role: FamilyRole = FamilyRole.MEMBER):
        family = Family(user_id=user_id, role=role)

        self.session.add(family)
        await self.session.commit()
        await self.session.refresh(family)

        return family


def get_family_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> FamilyRepository:
    return FamilyRepository(session)
