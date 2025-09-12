from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from dependencies.auth import get_current_user
from models.user import User
from schemas.user import UserProfileOut
from services.user import UserService, get_user_service

router = APIRouter(prefix="/users", tags=["user"])


@router.get(
    "/profile/",
    response_model=UserProfileOut,
    responses={
        401: {"description": "Unauthorized: authentication required"},
        404: {"description": "Not Found: user profile not found"},
    },
)
async def get_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    profile = await user_service.get_profile(current_user)
    return profile
