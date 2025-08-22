from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, status
from fastapi.params import Depends

from core.jwt import AuthJWTService, get_auth_jwt_service
from core.logging import logger
from enums.tags import RouterTags
from helpers.logging import anonymize_email
from schemas.token import TokenAccessOut, TokenPairOut, TokenRefreshIn
from schemas.user import UserAuthCredentialsIn, UserIn
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
    with logger.contextualize(email=anonymize_email(user_in.email)):
        logger.info("start register_user request")
        await service.register(user_in)

    return Response(status_code=status.HTTP_201_CREATED)


@router.post("/token/", response_model=TokenPairOut)
async def login(
    user_credentials: UserAuthCredentialsIn,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        with logger.contextualize(email=anonymize_email(user_credentials.email)):
            logger.info("start login request")
            return await user_service.login(user_credentials)
    except Exception:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)


@router.post("/token/refresh/", response_model=TokenAccessOut)
async def refresh_token(
    body: TokenRefreshIn,
    auth_jwt_service: Annotated[AuthJWTService, Depends(get_auth_jwt_service)],
):
    try:
        logger.info("start refresh_token request")
        return auth_jwt_service.renew_access_token(body.refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
