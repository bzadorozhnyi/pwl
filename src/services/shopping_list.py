import uuid
from typing import Annotated

from fastapi import Depends

from exceptions import ForbiddenException
from models.shopping_list import ShoppingList
from repositories.shopping_list import (
    ShoppingListRepository,
    get_shopping_list_repository,
)
from schemas.shopping_list import CreateShoppingListIn
from services.family import FamilyService, get_family_service


class ShoppingListService:
    def __init__(
        self,
        shopping_list_repository: ShoppingListRepository,
        family_service: FamilyService,
    ):
        self.shopping_list_repository = shopping_list_repository
        self.family_service = family_service

    async def create_shopping_list(
        self, list_data: CreateShoppingListIn, creator_id: uuid.UUID
    ) -> ShoppingList:
        await self._check_create_permissions(list_data, creator_id)

        shopping_list = ShoppingList(**list_data.model_dump(), creator_id=creator_id)

        return await self.shopping_list_repository.create(shopping_list)

    async def _check_create_permissions(
        self, list_data: CreateShoppingListIn, creator_id: str
    ):
        is_creator_family_member = await self.family_service.is_member(
            list_data.family_id, creator_id
        )
        if not is_creator_family_member:
            raise ForbiddenException("Creator is not member of family")


def get_shopping_list_service(
    shopping_list_repository: Annotated[
        ShoppingListRepository, Depends(get_shopping_list_repository)
    ],
    family_service: Annotated[FamilyService, Depends(get_family_service)],
) -> ShoppingListService:
    return ShoppingListService(shopping_list_repository, family_service)
