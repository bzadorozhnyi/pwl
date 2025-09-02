from typing import Annotated

from fastapi import APIRouter, Depends, status

from core.pagination import Paginator
from dependencies.auth import get_current_user
from dependencies.pagination import get_paginator
from models.user import User
from schemas.family_task import CreateFamilyTaskIn, FamilyTaskOut
from schemas.pagination import Paginated
from services.family_task import FamilyTaskService, get_family_task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=FamilyTaskOut,
    responses={
        403: {
            "description": "Forbidden: either the creator or the assignee is not a member of the family"
        }
    },
)
async def create_family_task(
    body: CreateFamilyTaskIn,
    current_user: Annotated[User, Depends(get_current_user)],
    family_task_service: Annotated[FamilyTaskService, Depends(get_family_task_service)],
):
    return await family_task_service.create_family_task(body, current_user.id)


@router.get(
    "/{family_id}/",
    status_code=status.HTTP_200_OK,
    response_model=Paginated[FamilyTaskOut],
    responses={403: {"description": "Forbidden: user is not a member of the family"}},
)
async def list_family_tasks(
    family_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    paginator: Annotated[Paginator, Depends(get_paginator)],
    family_task_service: Annotated[FamilyTaskService, Depends(get_family_task_service)],
):
    return await family_task_service.list_family_tasks(
        current_user.id, family_id, paginator
    )
