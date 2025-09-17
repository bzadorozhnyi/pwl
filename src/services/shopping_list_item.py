import uuid
from typing import Annotated

from fastapi.params import Depends

from core.pagination import Paginator
from exceptions import ForbiddenException, InputException, NotFoundException
from models.shopping_list_item import ShoppingListItem
from repositories.shopping_list import (
    ShoppingListRepository,
    get_shopping_list_repository,
)
from repositories.shopping_list_item import (
    ShoppingListItemRepository,
    get_shopping_list_item_repository,
)
from schemas.pagination import Paginated
from schemas.shopping_list_item import (
    CreateShoppingListItemIn,
    ShoppingListItemFilter,
    UpdatePurchasedStatusShoppingListItemIn,
)
from schemas.ws.server import (
    CreateShoppingListItemEvent,
    DeleteShoppingListItemEvent,
    DeleteShoppingListItemOut,
    ServerWebSocketEvent,
    UpdatePurchasedStatusOut,
    UpdatePurchasedStatusShoppingListItemEvent,
)
from services.family import FamilyService, get_family_service
from services.group_message import GroupMessageService, get_group_message_service


class ShoppingListItemService:
    def __init__(
        self,
        *,
        shopping_list_repository: ShoppingListRepository,
        shopping_list_item_repository: ShoppingListItemRepository,
        family_service: FamilyService,
        group_message_service: GroupMessageService,
    ):
        self.shopping_list_repository = shopping_list_repository
        self.shopping_list_item_repository = shopping_list_item_repository
        self.family_service = family_service
        self.group_message_service = group_message_service

    async def create_shopping_list_item(
        self, item_data: CreateShoppingListItemIn, user_id: uuid.UUID
    ) -> ShoppingListItem:
        await self._check_create_permissions(item_data, user_id)

        item = ShoppingListItem(**item_data.model_dump(), creator_id=user_id)

        item = await self.shopping_list_item_repository.create(item)

        await self._send_task_event(
            user_id,
            CreateShoppingListItemEvent(
                family_id=item.shopping_list.family_id,
                data=item,
            ),
        )

        return item

    async def _check_create_permissions(
        self, item_data: CreateShoppingListItemIn, user_id: uuid.UUID
    ):
        shopping_list = await self.shopping_list_repository.get_by_id(
            item_data.shopping_list_id
        )
        if shopping_list is None:
            raise NotFoundException("Shopping list not found")

        is_family_member = await self.family_service.is_member(
            shopping_list.family_id, user_id
        )

        if not is_family_member:
            raise ForbiddenException(
                "User is not allowed to add items to this shopping list"
            )

    async def get_all_shopping_list_items(
        self,
        shopping_list_id: str,
        user_id: uuid.UUID,
        filters: ShoppingListItemFilter,
        paginator: Paginator,
    ) -> Paginated[ShoppingListItem]:
        await self._check_get_all_shopping_list_items_permissions(
            shopping_list_id, user_id, filters
        )

        return await self.shopping_list_item_repository.get_all_by_shopping_list_id_paginated(
            shopping_list_id, filters, paginator
        )

    async def _check_get_all_shopping_list_items_permissions(
        self, shopping_list_id: str, user_id: uuid.UUID, filters: ShoppingListItemFilter
    ):
        shopping_list = await self.shopping_list_repository.get_by_id(shopping_list_id)
        if shopping_list is None:
            raise NotFoundException("Shopping list not found")

        is_family_member = await self.family_service.is_member(
            shopping_list.family_id, user_id
        )

        if not is_family_member:
            raise ForbiddenException(
                "User is not allowed to view items of this shopping list"
            )

        if filters.name and len(filters.name.split()) > 10:
            raise InputException("Too many words in search filter")

    async def update_shopping_list_item_purchase_status(
        self,
        item_id: str,
        body: UpdatePurchasedStatusShoppingListItemIn,
        user_id: uuid.UUID,
    ) -> None:
        item = await self.shopping_list_item_repository.get_by_id(uuid.UUID(item_id))
        await self._check_update_permissions(item, user_id)

        item.purchased = body.purchased
        await self.shopping_list_item_repository.update(item)

        await self._send_task_event(
            user_id,
            UpdatePurchasedStatusShoppingListItemEvent(
                family_id=item.shopping_list.family_id,
                data=UpdatePurchasedStatusOut(id=item.id, purchased=item.purchased),
            ),
        )

    async def _check_update_permissions(
        self, item: ShoppingListItem, user_id: uuid.UUID
    ):
        if item is None:
            raise NotFoundException("Shopping list item not found")

        shopping_list = await self.shopping_list_repository.get_by_id(
            item.shopping_list_id
        )
        if shopping_list is None:
            raise NotFoundException("Shopping list not found")

        is_family_member = await self.family_service.is_member(
            shopping_list.family_id, user_id
        )

        if not is_family_member:
            raise ForbiddenException(
                "User is not allowed to update items of this shopping list"
            )

    async def delete_shopping_list_item(self, item_id: str, user_id: uuid.UUID):
        item = await self.shopping_list_item_repository.get_by_id(uuid.UUID(item_id))
        await self._check_delete_permissions(item, user_id)

        await self.shopping_list_item_repository.delete(item)

        await self._send_task_event(
            user_id,
            DeleteShoppingListItemEvent(
                family_id=item.shopping_list.family_id,
                data=DeleteShoppingListItemOut(id=item.id),
            ),
        )

    async def _check_delete_permissions(
        self, item: ShoppingListItem, user_id: uuid.UUID
    ):
        if item is None:
            raise NotFoundException("Shopping list item not found")

        shopping_list = await self.shopping_list_repository.get_by_id(
            item.shopping_list_id
        )
        if shopping_list is None:
            raise NotFoundException("Shopping list not found")

        is_family_member = await self.family_service.is_member(
            shopping_list.family_id, user_id
        )

        if not is_family_member:
            raise ForbiddenException(
                "User is not allowed to delete items of this shopping list"
            )

    async def _send_task_event(self, user_id: uuid.UUID, event: ServerWebSocketEvent):
        await self.group_message_service.send_to_family(
            user_id, event.model_dump(mode="json")
        )


def get_shopping_list_item_service(
    shopping_list_repository: Annotated[
        ShoppingListRepository, Depends(get_shopping_list_repository)
    ],
    shopping_list_item_repository: Annotated[
        ShoppingListItemRepository, Depends(get_shopping_list_item_repository)
    ],
    family_service: Annotated[FamilyService, Depends(get_family_service)],
    group_message_service: Annotated[
        GroupMessageService, Depends(get_group_message_service)
    ],
) -> ShoppingListItemService:
    return ShoppingListItemService(
        shopping_list_item_repository=shopping_list_item_repository,
        shopping_list_repository=shopping_list_repository,
        family_service=family_service,
        group_message_service=group_message_service,
    )
