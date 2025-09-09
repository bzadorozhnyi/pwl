from typing import Annotated

from fastapi import APIRouter, Depends, status

from core.pagination import Paginator
from dependencies.auth import get_current_user
from dependencies.pagination import get_paginator
from models.user import User
from schemas.pagination import Paginated
from schemas.shopping_list_item import (
    CreateShoppingListItemIn,
    ShoppingListItemOut,
)
from services.shopping_list_item import (
    ShoppingListItemService,
    get_shopping_list_item_service,
)

router = APIRouter(prefix="/shopping-list-items", tags=["shopping-list-items"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ShoppingListItemOut,
    responses={
        403: {"description": "Forbidden: user is not a member of the family"},
        404: {"description": "Shopping list not found"},
    },
)
async def create_shopping_list_item(
    body: CreateShoppingListItemIn,
    current_user: Annotated[User, Depends(get_current_user)],
    shopping_list_item_service: Annotated[
        ShoppingListItemService, Depends(get_shopping_list_item_service)
    ],
):
    return await shopping_list_item_service.create_shopping_list_item(
        body, current_user.id
    )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=Paginated[ShoppingListItemOut],
    responses={
        403: {"description": "Forbidden: user is not a member of the family"},
        404: {"description": "Shopping list not found"},
    },
)
async def get_all_shopping_list_items(
    shopping_list_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    paginator: Annotated[Paginator, Depends(get_paginator)],
    shopping_list_item_service: Annotated[
        ShoppingListItemService, Depends(get_shopping_list_item_service)
    ],
):
    return await shopping_list_item_service.get_all_shopping_list_items(
        shopping_list_id, current_user.id, paginator
    )
