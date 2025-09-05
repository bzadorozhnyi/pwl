from typing import Annotated

from fastapi import WebSocket
from fastapi.params import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from models.user import User
from security import WebSocketBearer
from services.user import UserService, get_user_service

bearer_scheme = HTTPBearer()


async def get_current_user(
    token_credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    token = token_credentials.credentials
    return await user_service.get_user_from_token(token)


websocket_bearer_scheme = WebSocketBearer()


async def get_current_websocket_user(
    websocket: WebSocket,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User | None:
    print("Getting token credentials from WebSocket...")
    token_credentials = await websocket_bearer_scheme(websocket)
    print("Token credentials:", token_credentials)
    if token_credentials is None:
        return None
    token = token_credentials.credentials
    return await user_service.get_user_from_token(token)
