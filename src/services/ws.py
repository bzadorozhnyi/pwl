from typing import Annotated

from fastapi import Depends

from ws.group_manager.base import WebSocketGroupManager
from ws.group_manager.in_memory import InMemoryWebSocketGroupManager


class WebSocketService:
    def __init__(self, group_manager: WebSocketGroupManager):
        self.group_manager = group_manager

    async def group_add(self, group: str, websocket):
        await self.group_manager.group_add(group, websocket)

    async def group_leave(self, group: str, websocket):
        await self.group_manager.group_discard(group, websocket)

    async def receive_from_connection(self, websocket) -> str:
        return await websocket.receive_text()

    async def send_to_group(self, group: str, message: dict):
        await self.group_manager.group_send(group, message)


def get_websocket_group_manager() -> WebSocketGroupManager:
    return InMemoryWebSocketGroupManager()


def get_websocket_service(
    websocket_group_manager: Annotated[
        WebSocketGroupManager, Depends(get_websocket_group_manager)
    ],
) -> WebSocketService:
    return WebSocketService(websocket_group_manager)
