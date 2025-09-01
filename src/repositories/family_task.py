from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_session
from models.family_task import FamilyTask


class FamilyTaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, family_task: FamilyTask):
        self.session.add(family_task)
        await self.session.commit()
        await self.session.refresh(family_task)

        return family_task


def get_family_task_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> FamilyTaskRepository:
    return FamilyTaskRepository(session)
