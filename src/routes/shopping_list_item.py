from typing import Annotated

from fastapi import APIRouter, Depends, status

from dependencies.auth import get_current_user
from models.user import User
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
