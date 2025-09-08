from typing import Annotated

from fastapi import APIRouter, Depends, status

from dependencies.auth import get_current_user
from models.user import User
from schemas.shopping_list import CreateShoppingListIn, ShoppingListOut
from services.shopping_list import ShoppingListService, get_shopping_list_service

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
