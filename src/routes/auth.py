from typing import Annotated

from fastapi import APIRouter, Response, status
from fastapi.params import Depends

from core.jwt import AuthJWTService, get_auth_jwt_service
from schemas.password_reset import RequestForgotPasswordIn, UpdateForgottenPasswordIn
from schemas.token import TokenAccessOut, TokenRefreshIn
from schemas.user import UserAuthCredentialsIn, UserIn, UserWithTokensOut
from services.password_reset import PasswordResetService, get_password_reset_service
from services.user import UserService, get_user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserWithTokensOut,
    responses={
        400: {"description": "Email already registered"},
    },
)
async def register_user(
    user_in: UserIn, service: Annotated[UserService, Depends(get_user_service)]
):
    return await service.register(user_in)


@router.post(
    "/token/",
    responses={401: {"description": "Invalid identifier or password"}},
    response_model=UserWithTokensOut,
)
async def login(
    user_credentials: UserAuthCredentialsIn,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.login(user_credentials)


@router.post(
    "/token/refresh/",
    responses={401: {"description": "Invalid refresh token"}},
    response_model=TokenAccessOut,
)
async def refresh_token(
    body: TokenRefreshIn,
    auth_jwt_service: Annotated[AuthJWTService, Depends(get_auth_jwt_service)],
):
    return auth_jwt_service.renew_access_token(body.refresh_token)


@router.post("/forgot-password/")
async def forgot_password(
    body: RequestForgotPasswordIn,
    password_reset_service: Annotated[
        PasswordResetService, Depends(get_password_reset_service)
    ],
):
    await password_reset_service.request_forgot_password(body.email)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/reset-password/")
async def reset_password(
    body: UpdateForgottenPasswordIn,
    password_reset_service: Annotated[
        PasswordResetService, Depends(get_password_reset_service)
    ],
):
    await password_reset_service.update_forgotten_password(
        body.token, body.new_password
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
