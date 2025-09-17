from typing import Annotated

from fastapi import APIRouter, Depends

from dependencies.auth import get_current_user
from models.user import User
from schemas.recipe import RecipeRequestIn, RecipeResponse
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
    return await recipe_service.get_ingredients_for_recipe(body.request)
