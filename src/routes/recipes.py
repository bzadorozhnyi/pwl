from typing import Annotated

from fastapi import APIRouter, Depends

from dependencies.auth import get_current_user
from models.user import User
from schemas.recipe import (
    RecipeMergeRequestIn,
    RecipeRequestIn,
    RecipeResponse,
    UpdateShoppingListWithRecipeResponse,
)
from services.recipe import RecipeService, get_recipe_service

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post(
    "/",
    response_model=RecipeResponse,
    responses={
        500: {
            "description": "Internal Server Error: Unexpected error during recipe generation."
        },
        502: {"description": "Bad Gateway: LLM retry error"},
    },
)
async def get_ingredients_for_recipe(
    body: RecipeRequestIn,
    current_user: Annotated[User, Depends(get_current_user)],
    recipe_service: Annotated[RecipeService, Depends(get_recipe_service)],
):
    return await recipe_service.get_ingredients_for_recipe(body.recipe_request)


@router.post(
    "/merge-with-shopping-list/",
    response_model=UpdateShoppingListWithRecipeResponse,
    responses={
        403: {"description": "Forbidden: user is not a member of the family"},
        404: {"description": "Not Found: shopping list not found"},
        500: {
            "description": "Internal Server Error: Unexpected error during recipe generation."
        },
        502: {"description": "Bad Gateway: LLM retry error"},
    },
)
async def get_ingredients_and_merge_with_shopping_list(
    body: RecipeMergeRequestIn,
    current_user: Annotated[User, Depends(get_current_user)],
    recipe_service: Annotated[RecipeService, Depends(get_recipe_service)],
):
    return await recipe_service.get_ingredients_and_merge_with_shopping_list(
        body, current_user.id
    )
