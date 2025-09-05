import uuid
from typing import Annotated

from fastapi import Depends

from core.logging import logger
from repositories.family import FamilyRepository, get_family_repository
from services.ws import WebSocketService, get_websocket_service


class GroupMessageService:
    def __init__(
        self, websocket_service: WebSocketService, family_repository: FamilyRepository
    ):
        self.websocket_service = websocket_service
        self.family_repository = family_repository

    async def _get_family_group_name(self, user_id: uuid.UUID) -> str:
        user_families = await self.family_repository.get_user_families(user_id)

        if not user_families:
            logger.error(f"User {user_id} has no families")

        return f"family.{user_families[0]}"

    async def add_to_family(self, user_id: uuid.UUID, websocket):
        group_name = await self._get_family_group_name(user_id)
        await self.websocket_service.group_add(group_name, websocket)

    async def send_to_family(self, user_id: uuid.UUID, message: dict):
        group_name = await self._get_family_group_name(user_id)
        await self.websocket_service.send_to_group(group_name, message)


def get_group_message_service(
    websocket_service: Annotated[WebSocketService, Depends(get_websocket_service)],
    family_repository: Annotated[FamilyRepository, Depends(get_family_repository)],
) -> GroupMessageService:
    return GroupMessageService(websocket_service, family_repository)
