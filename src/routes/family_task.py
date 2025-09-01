from typing import Annotated

from fastapi import APIRouter, Depends, status

from dependencies.auth import get_current_user
from models.user import User
from schemas.family_task import CreateFamilyTaskIn
from services.family_task import FamilyTaskService, get_family_task_service

router = APIRouter(prefix="/family-tasks", tags=["family-tasks"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_family_task(
    body: CreateFamilyTaskIn,
    current_user: Annotated[User, Depends(get_current_user)],
    family_task_service: Annotated[FamilyTaskService, Depends(get_family_task_service)],
):
    return await family_task_service.create_family_task(body, current_user.id)
