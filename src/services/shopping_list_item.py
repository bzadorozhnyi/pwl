import uuid
from typing import Annotated

from fastapi.params import Depends

from exceptions import ForbiddenException, NotFoundException
from models.shopping_list_item import ShoppingListItem
from repositories.shopping_list import (
    ShoppingListRepository,
    get_shopping_list_repository,
)
from repositories.shopping_list_item import (
    ShoppingListItemRepository,
    get_shopping_list_item_repository,
)
from schemas.shopping_list_item import CreateShoppingListItemIn
from services.family import FamilyService, get_family_service


class ShoppingListItemService:
    def __init__(
        self,
        *,
        shopping_list_repository: ShoppingListRepository,
        shopping_list_item_repository: ShoppingListItemRepository,
        family_service: FamilyService,
    ):
        self.shopping_list_repository = shopping_list_repository
        self.shopping_list_item_repository = shopping_list_item_repository
        self.family_service = family_service

    async def create_shopping_list_item(
        self, item_data: CreateShoppingListItemIn, user_id: uuid.UUID
    ):
        await self._check_create_permissions(item_data, user_id)

        item = ShoppingListItem(**item_data.model_dump(), creator_id=user_id)
        return await self.shopping_list_item_repository.create(item)

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


def get_shopping_list_item_service(
    shopping_list_repository: Annotated[
        ShoppingListRepository, Depends(get_shopping_list_repository)
    ],
    shopping_list_item_repository: Annotated[
        ShoppingListItemRepository, Depends(get_shopping_list_item_repository)
    ],
    family_service: Annotated[FamilyService, Depends(get_family_service)],
) -> ShoppingListItemService:
    return ShoppingListItemService(
        shopping_list_item_repository=shopping_list_item_repository,
        shopping_list_repository=shopping_list_repository,
        family_service=family_service,
    )
