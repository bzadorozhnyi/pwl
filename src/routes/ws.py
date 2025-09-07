from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket

from dependencies.auth import get_current_websocket_user
from models.user import User
from services.group_message import GroupMessageService, get_group_message_service
from services.ws import WebSocketService, get_websocket_service

router = APIRouter()


@router.websocket("/ws/")
async def websocket_endpoint(
    websocket: WebSocket,
    current_user: Annotated[User | None, Depends(get_current_websocket_user)],
    websocket_service: Annotated[WebSocketService, Depends(get_websocket_service)],
    group_message_service: Annotated[
        GroupMessageService, Depends(get_group_message_service)
    ],
):
    if current_user is None:
        return

    await group_message_service.add_to_family(current_user.id, websocket)

    while True:
        await websocket_service.receive_from_connection(websocket)
