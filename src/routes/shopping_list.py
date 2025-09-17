from typing import Annotated

from fastapi import APIRouter, Depends, status

from core.pagination import Paginator
from dependencies.auth import get_current_user
from dependencies.pagination import get_paginator
from models.user import User
from schemas.pagination import Paginated
from schemas.shopping_list import (
    CreateShoppingListFromIngredientsIn,
    CreateShoppingListIn,
    ShoppingListOut,
    UpdateShoppingListIn,
)
from schemas.shopping_list_item import ShoppingListItemFilter, ShoppingListItemOut
from services.shopping_list import ShoppingListService, get_shopping_list_service
from services.shopping_list_item import (
    ShoppingListItemService,
    get_shopping_list_item_service,
)

router = APIRouter(prefix="/shopping-lists", tags=["shopping-lists"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ShoppingListOut,
    responses={403: {"description": "Forbidden: user is not a member of the family"}},
)
async def create_shopping_list(
    body: CreateShoppingListIn,
    current_user: Annotated[User, Depends(get_current_user)],
    shopping_list_service: Annotated[
        ShoppingListService, Depends(get_shopping_list_service)
    ],
):
    return await shopping_list_service.create_shopping_list(body, current_user.id)


@router.post(
    "/from-ingredients/",
    status_code=status.HTTP_201_CREATED,
    response_model=ShoppingListOut,
    responses={403: {"description": "Forbidden: user is not a member of the family"}},
)
async def create_shopping_list_from_ingredients(
    body: CreateShoppingListFromIngredientsIn,
    current_user: Annotated[User, Depends(get_current_user)],
    shopping_list_service: Annotated[
        ShoppingListService, Depends(get_shopping_list_service)
    ],
):
    return await shopping_list_service.create_shopping_list_from_ingredients(
        body, current_user.id
    )


@router.get(
    "/{family_id}/",
    status_code=status.HTTP_200_OK,
    response_model=Paginated[ShoppingListOut],
    responses={403: {"description": "Forbidden: user is not a member of the family"}},
)
async def list_shopping_lists(
    family_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    paginator: Annotated[Paginator, Depends(get_paginator)],
    shopping_list_service: Annotated[
        ShoppingListService, Depends(get_shopping_list_service)
    ],
):
    return await shopping_list_service.list_shopping_lists(
        current_user.id, family_id, paginator
    )


@router.get(
    "/{shopping_list_id}/items/",
    status_code=status.HTTP_200_OK,
    response_model=Paginated[ShoppingListItemOut],
    responses={
        400: {"description": "Bad Request: invalid filter parameters"},
        403: {"description": "Forbidden: user is not a member of the family"},
        404: {"description": "Not Found: shopping list not found"},
    },
)
async def get_all_shopping_list_items(
    shopping_list_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    filters: Annotated[ShoppingListItemFilter, Depends()],
    paginator: Annotated[Paginator, Depends(get_paginator)],
    shopping_list_item_service: Annotated[
        ShoppingListItemService, Depends(get_shopping_list_item_service)
    ],
):
    return await shopping_list_item_service.get_all_shopping_list_items(
        shopping_list_id, current_user.id, filters, paginator
    )


@router.put(
    "/{shopping_list_id}/",
    status_code=status.HTTP_200_OK,
    response_model=ShoppingListOut,
    responses={
        403: {"description": "Forbidden: user is not a member of the family"},
        404: {"description": "Not Found: shopping list does not exist"},
    },
)
async def update_shopping_list(
    shopping_list_id: str,
    body: UpdateShoppingListIn,
    current_user: Annotated[User, Depends(get_current_user)],
    shopping_list_service: Annotated[
        ShoppingListService, Depends(get_shopping_list_service)
    ],
):
    return await shopping_list_service.update_shopping_list(
        shopping_list_id, body, current_user.id
    )


@router.delete(
    "/{shopping_list_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        403: {"description": "Forbidden: user is not a member of the family"},
        404: {"description": "Not Found: shopping list does not exist"},
    },
)
async def delete_shopping_list(
    shopping_list_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    shopping_list_service: Annotated[
        ShoppingListService, Depends(get_shopping_list_service)
    ],
):
    await shopping_list_service.delete_shopping_list(shopping_list_id, current_user)
