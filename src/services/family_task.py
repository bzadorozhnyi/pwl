import uuid
from typing import Annotated

from fastapi import Depends

from core.pagination import Paginator
from exceptions import ForbiddenException
from models.family_task import FamilyTask
from repositories.family_task import FamilyTaskRepository, get_family_task_repository
from schemas.family_task import (
    CreateFamilyTaskIn,
)
from schemas.pagination import Paginated
from services.family import FamilyService, get_family_service


class FamilyTaskService:
    def __init__(
        self,
        family_task_repository: FamilyTaskRepository,
        family_service: FamilyService,
    ):
        self.family_task_repository = family_task_repository
        self.family_service = family_service

    async def create_family_task(
        self, family_task_data: CreateFamilyTaskIn, creator_id: uuid.UUID
    ) -> FamilyTask:
        is_creator_family_member = await self.family_service.is_member(
            family_task_data.family_id, creator_id
        )
        if not is_creator_family_member:
            raise ForbiddenException("Creator is not member of family")

        is_assignee_family_member = await self.family_service.is_member(
            family_task_data.family_id, family_task_data.assignee_id
        )
        if not is_assignee_family_member:
            raise ForbiddenException("Assignee is not member of family")

        family_task = FamilyTask(**family_task_data.model_dump(), creator_id=creator_id)

        return await self.family_task_repository.create(family_task)

    async def list_family_tasks(
        self, user_id: uuid.UUID, family_id: str, paginator: Paginator
    ) -> Paginated[FamilyTask]:
        is_member = await self.family_service.is_member(uuid.UUID(family_id), user_id)
        if not is_member:
            raise ForbiddenException("User is not member of family")

        family_tasks = await self.family_task_repository.list_by_family_id(
            uuid.UUID(family_id), paginator
        )
        return family_tasks


def get_family_task_service(
    family_task_repository: Annotated[
        FamilyTaskRepository, Depends(get_family_task_repository)
    ],
    family_service: Annotated[FamilyService, Depends(get_family_service)],
) -> FamilyTaskService:
    return FamilyTaskService(
        family_task_repository=family_task_repository, family_service=family_service
    )
