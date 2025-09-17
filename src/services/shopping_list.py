import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_session
from core.pagination import Paginator
from exceptions import ForbiddenException, NotFoundException
from models.shopping_list import ShoppingList
from models.shopping_list_item import ShoppingListItem
from models.user import User
from repositories.shopping_list import (
    ShoppingListRepository,
    get_shopping_list_repository,
)
from repositories.shopping_list_item import (
    ShoppingListItemRepository,
    get_shopping_list_item_repository,
)
from schemas.pagination import Paginated
from schemas.shopping_list import (
    CreateShoppingListFromIngredientsIn,
    CreateShoppingListIn,
    UpdateShoppingListIn,
)
from schemas.ws.server import (
    CreateShoppingListEvent,
    DeleteShoppingListEvent,
    DeleteShoppingListOut,
    ServerWebSocketEvent,
    UpdateShoppingListEvent,
)
from services.family import FamilyService, get_family_service
from services.group_message import GroupMessageService, get_group_message_service


class ShoppingListService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        shopping_list_repository: ShoppingListRepository,
        shopping_list_item_repository: ShoppingListItemRepository,
        family_service: FamilyService,
        group_message_service: GroupMessageService,
    ):
        self.session = session
        self.shopping_list_repository = shopping_list_repository
        self.shopping_list_item_repository = shopping_list_item_repository
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

    async def create_shopping_list_from_ingredients(
        self,
        ingredients_list_data: CreateShoppingListFromIngredientsIn,
        creator_id: uuid.UUID,
    ) -> ShoppingList:
        shopping_list_data = CreateShoppingListIn(
            name=ingredients_list_data.title, family_id=ingredients_list_data.family_id
        )

        await self._check_create_permissions(shopping_list_data, creator_id)

        shopping_list = ShoppingList(
            **shopping_list_data.model_dump(), creator_id=creator_id
        )

        async with self.session.transaction():
            shopping_list = await self.shopping_list_repository.create(shopping_list)

            items = [
                ShoppingListItem(
                    name=ingredient.name,
                    shopping_list_id=shopping_list.id,
                    creator_id=creator_id,
                )
                for ingredient in ingredients_list_data.ingredients
            ]

            await self.shopping_list_item_repository.create_batch(items)

        await self._send_task_event(
            creator_id,
            CreateShoppingListEvent(
                family_id=shopping_list.family_id,
                data=shopping_list,
            ),
        )

        return shopping_list

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

        shopping_list = await self.shopping_list_repository.update(shopping_list)

        await self._send_task_event(
            user_id,
            UpdateShoppingListEvent(
                family_id=shopping_list.family_id,
                data=shopping_list,
            ),
        )

        return shopping_list

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

    async def delete_shopping_list(self, shopping_list_id: str, user: User):
        shopping_list = await self.shopping_list_repository.get_by_id(
            uuid.UUID(shopping_list_id)
        )
        await self._check_delete_permissions(shopping_list, user.id)

        await self.shopping_list_repository.delete(shopping_list)

        await self._send_task_event(
            user.id,
            DeleteShoppingListEvent(
                family_id=shopping_list.family_id,
                data=DeleteShoppingListOut(id=shopping_list.id),
            ),
        )

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
    session: Annotated[AsyncSession, Depends(get_session)],
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
) -> ShoppingListService:
    return ShoppingListService(
        session=session,
        shopping_list_repository=shopping_list_repository,
        shopping_list_item_repository=shopping_list_item_repository,
        family_service=family_service,
        group_message_service=group_message_service,
    )
