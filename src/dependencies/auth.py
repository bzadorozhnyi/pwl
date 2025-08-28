from typing import Annotated

from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer

from models.user import User
from services.user import UserService, get_user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token/")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    return await user_service.get_user_from_token(token)
