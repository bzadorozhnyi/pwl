import uuid
from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.db import get_session
from core.pagination import Paginator
from models.family_task import FamilyTask
from schemas.pagination import Paginated


class FamilyTaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, family_task: FamilyTask) -> FamilyTask:
        self.session.add(family_task)
        await self.session.commit()
        await self.session.refresh(family_task)

        return family_task

    async def get_by_id(self, id: uuid.UUID) -> FamilyTask | None:
        statement = select(FamilyTask).where(FamilyTask.id == id)

        return await self.session.scalar(statement)

    async def update(self, family_task: FamilyTask) -> FamilyTask:
        family_task.updated_at = datetime.now()

        self.session.add(family_task)
        await self.session.commit()
        await self.session.refresh(family_task)

        return family_task

    async def list_by_family_id(
        self, family_id: uuid.UUID, paginator: Paginator
    ) -> Paginated[FamilyTask]:
        return await paginator.paginate(
            select(FamilyTask).where(FamilyTask.family_id == family_id)
        )


def get_family_task_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> FamilyTaskRepository:
    return FamilyTaskRepository(session)
