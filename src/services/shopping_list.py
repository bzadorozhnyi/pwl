import uuid
from typing import Annotated

from fastapi import Depends

from core.pagination import Paginator
from exceptions import ForbiddenException, NotFoundException
from models.shopping_list import ShoppingList
from repositories.shopping_list import (
    ShoppingListRepository,
    get_shopping_list_repository,
)
from schemas.pagination import Paginated
from schemas.shopping_list import CreateShoppingListIn, UpdateShoppingListIn
from schemas.ws.server import CreateShoppingListEvent, ServerWebSocketEvent
from services.family import FamilyService, get_family_service
from services.group_message import GroupMessageService, get_group_message_service


class ShoppingListService:
    def __init__(
        self,
        *,
        shopping_list_repository: ShoppingListRepository,
        family_service: FamilyService,
        group_message_service: GroupMessageService,
    ):
        self.shopping_list_repository = shopping_list_repository
        self.family_service = family_service
        self.group_message_service = group_message_service

    async def create_shopping_list(
        self, list_data: CreateShoppingListIn, creator_id: uuid.UUID
    ) -> ShoppingList:
        await self._check_create_permissions(list_data, creator_id)

        shopping_list = ShoppingList(**list_data.model_dump(), creator_id=creator_id)

        shopping_list = await self.shopping_list_repository.create(shopping_list)

        await self._send_task_event(
            creator_id,
            CreateShoppingListEvent(
                family_id=shopping_list.family_id,
                data=shopping_list,
            ),
        )

        return shopping_list

    async def _check_create_permissions(
        self, list_data: CreateShoppingListIn, creator_id: str
    ):
        is_creator_family_member = await self.family_service.is_member(
            list_data.family_id, creator_id
        )
        if not is_creator_family_member:
            raise ForbiddenException("Creator is not member of family")

    async def list_shopping_lists(
        self, user_id: uuid.UUID, family_id: str, paginator: Paginator
    ) -> Paginated[ShoppingList]:
        await self._check_list_permissions(uuid.UUID(family_id), user_id)

        return await self.shopping_list_repository.list_by_family_id(
            uuid.UUID(family_id), paginator
        )

    async def _check_list_permissions(self, family_id: str, user_id: str):
        is_family_member = await self.family_service.is_member(family_id, user_id)
        if not is_family_member:
            raise ForbiddenException("User is not member of family")

    async def update_shopping_list(
        self,
        shopping_list_id: str,
        update_data: UpdateShoppingListIn,
        user_id: uuid.UUID,
    ) -> ShoppingList:
        shopping_list = await self.shopping_list_repository.get_by_id(
            uuid.UUID(shopping_list_id)
        )
        await self._check_update_permissions(shopping_list, user_id)

        update_data = update_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(shopping_list, key, value)

        return await self.shopping_list_repository.update(shopping_list)

    async def _check_update_permissions(
        self, shopping_list: ShoppingList, user_id: str
    ):
        if not shopping_list:
            raise NotFoundException("Shopping list not found")

        is_family_member = await self.family_service.is_member(
            shopping_list.family_id, user_id
        )
        if not is_family_member:
            raise ForbiddenException("User is not member of family")

    async def delete_shopping_list(self, shopping_list_id: str, user_id: uuid.UUID):
        shopping_list = await self.shopping_list_repository.get_by_id(
            uuid.UUID(shopping_list_id)
        )
        await self._check_delete_permissions(shopping_list, user_id)

        await self.shopping_list_repository.delete(shopping_list)

    async def _check_delete_permissions(
        self, shopping_list: ShoppingList, user_id: str
    ):
        if not shopping_list:
            raise NotFoundException("Shopping list not found")

        is_family_member = await self.family_service.is_member(
            shopping_list.family_id, user_id
        )
        if not is_family_member:
            raise ForbiddenException("User is not member of family")

    async def _send_task_event(self, user_id: uuid.UUID, event: ServerWebSocketEvent):
        await self.group_message_service.send_to_family(
            user_id, event.model_dump(mode="json")
        )


def get_shopping_list_service(
    shopping_list_repository: Annotated[
        ShoppingListRepository, Depends(get_shopping_list_repository)
    ],
    family_service: Annotated[FamilyService, Depends(get_family_service)],
    group_message_service: Annotated[
        GroupMessageService, Depends(get_group_message_service)
    ],
) -> ShoppingListService:
    return ShoppingListService(
        shopping_list_repository=shopping_list_repository,
        family_service=family_service,
        group_message_service=group_message_service,
    )
