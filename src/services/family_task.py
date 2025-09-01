import uuid
from typing import Annotated

from fastapi import Depends

from exceptions import ForbiddenException
from models.family_task import FamilyTask
from repositories.family_task import FamilyTaskRepository, get_family_task_repository
from schemas.family_task import CreateFamilyTaskIn, FamilyTaskOut
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
    ) -> FamilyTaskOut:
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
        family_task = await self.family_task_repository.create(family_task)

        return FamilyTaskOut(**family_task.model_dump())


def get_family_task_service(
    family_task_repository: Annotated[
        FamilyTaskRepository, Depends(get_family_task_repository)
    ],
    family_service: Annotated[FamilyService, Depends(get_family_service)],
) -> FamilyTaskService:
    return FamilyTaskService(
        family_task_repository=family_task_repository, family_service=family_service
    )
