from typing import Annotated

from fastapi import APIRouter, Response, status
from fastapi.params import Depends

from enums.tags import RouterTags
from schemas.user import UserIn
from services.user import UserService, get_user_service

router = APIRouter(tags=[RouterTags.AUTH])


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Email already registered"},
    },
)
async def register_user(
    user_in: UserIn, service: Annotated[UserService, Depends(get_user_service)]
):
    await service.register(user_in)
    return Response(status_code=status.HTTP_201_CREATED)
