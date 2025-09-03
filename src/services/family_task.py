import uuid
from typing import Annotated

from fastapi import Depends

from core.pagination import Paginator
from exceptions import ForbiddenException, InputException, NotFoundException
from models.family import FamilyRole
from models.family_task import FamilyTask
from models.user import User
from repositories.family_task import FamilyTaskRepository, get_family_task_repository
from schemas.family_task import CreateFamilyTaskIn, UpdateFamilyTaskIn
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

    async def update_family_task(
        self, task_id: str, update_data: UpdateFamilyTaskIn, user_id: uuid.UUID
    ) -> FamilyTask:
        family_task = await self.family_task_repository.get_by_id(uuid.UUID(task_id))
        await self._check_update_permissions(family_task, update_data, user_id)

        update_data = update_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(family_task, key, value)

        return await self.family_task_repository.update(family_task)

    async def _check_update_permissions(
        self,
        family_task: FamilyTask,
        update_data: UpdateFamilyTaskIn,
        user_id: uuid.UUID,
    ) -> FamilyTask:
        if not family_task:
            raise NotFoundException("Family task not found")

        if family_task.creator_id != user_id:
            raise ForbiddenException("Only the creator can update the task")

        if (
            update_data.assignee_id is not None
            and not await self.family_service.is_member(
                family_task.family_id, update_data.assignee_id
            )
        ):
            raise InputException("Assignee is not a member of the family")

    async def update_task_done(self, task_id: str, done: bool, user_id: uuid.UUID):
        family_task = await self.family_task_repository.get_by_id(uuid.UUID(task_id))
        await self._check_update_done_permissions(family_task, user_id)

        family_task.done = done
        await self.family_task_repository.update(family_task)

    async def _check_update_done_permissions(
        self,
        family_task: FamilyTask,
        user_id: uuid.UUID,
    ):
        if not family_task:
            raise NotFoundException("Family task not found")

        is_member = await self.family_service.is_member(family_task.family_id, user_id)
        if not is_member:
            raise ForbiddenException("User is not member of family")

        if family_task.creator_id != user_id and family_task.assignee_id != user_id:
            raise ForbiddenException("Only the creator or assignee can update the task")

    async def delete_family_task(self, task_id: str, user: User):
        family_task = await self.family_task_repository.get_by_id(uuid.UUID(task_id))
        await self._check_delete_permissions(family_task, user)

        await self.family_task_repository.delete(family_task)

    async def _check_delete_permissions(
        self,
        family_task: FamilyTask,
        user: User,
    ):
        if not family_task:
            raise NotFoundException("Family task not found")

        is_member = await self.family_service.is_member(family_task.family_id, user.id)
        if not is_member:
            raise ForbiddenException("User is not member of family")

        user_role = await self.family_service.get_user_role(
            family_task.family_id, user.id
        )

        if family_task.creator_id != user.id and user_role != FamilyRole.ADMIN:
            raise ForbiddenException("Only the creator or admin can delete the task")


def get_family_task_service(
    family_task_repository: Annotated[
        FamilyTaskRepository, Depends(get_family_task_repository)
    ],
    family_service: Annotated[FamilyService, Depends(get_family_service)],
) -> FamilyTaskService:
    return FamilyTaskService(
        family_task_repository=family_task_repository, family_service=family_service
    )
