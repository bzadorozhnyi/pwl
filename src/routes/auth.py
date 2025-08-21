from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, status
from fastapi.params import Depends

from core.jwt import AuthJWTService, get_auth_jwt_service
from enums.tags import RouterTags
from schemas.token import TokenAccessOut, TokenPairOut, TokenRefreshIn
from schemas.user import UserIn, UserLoginCredentials
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


@router.post("/token/", response_model=TokenPairOut)
async def login(
    user_credentials: UserLoginCredentials,
    user_service: Annotated[UserService, Depends(get_user_service)],
    auth_jwt_service: Annotated[AuthJWTService, Depends(get_auth_jwt_service)],
):
    user = await user_service.authenticate_user(user_credentials)
    if not user:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)

    return auth_jwt_service.create_token_pair({"sub": user.id})


@router.post("/token/refresh/", response_model=TokenAccessOut)
async def refresh_token(
    body: TokenRefreshIn,
    auth_jwt_service: Annotated[AuthJWTService, Depends(get_auth_jwt_service)],
):
    try:
        payload = auth_jwt_service.decode_refresh_token(body.refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    return TokenAccessOut(
        access_token=auth_jwt_service.create_access_token({"sub": payload["sub"]})
    )
