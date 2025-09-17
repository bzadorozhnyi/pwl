import os
import uuid
from typing import Annotated

from fastapi import Depends
from pydantic_ai import (
    Agent,
    ModelRetry,
    ModelSettings,
    PromptedOutput,
    RunContext,
    Tool,
)

from core.config import settings
from core.logging import logger
from exceptions import (
    BadGatewayException,
    ForbiddenException,
    InternalException,
    NotFoundException,
)
from repositories.family import FamilyRepository, get_family_repository
from repositories.shopping_list import (
    ShoppingListRepository,
    get_shopping_list_repository,
)
from repositories.shopping_list_item import (
    ShoppingListItemRepository,
    get_shopping_list_item_repository,
)
from schemas.recipe import (
    RecipeMergeAgentDeps,
    RecipeMergeRequestIn,
    RecipeMergeShoppingListItem,
    RecipeResponse,
    UpdateShoppingListWithRecipeResponse,
)


class RecipeService:
    def __init__(
        self,
        *,
        family_repository: FamilyRepository,
        shopping_list_repository: ShoppingListRepository,
        shopping_list_item_repository: ShoppingListItemRepository,
    ):
        self.family_repository = family_repository
        self.shopping_list_repository = shopping_list_repository
        self.shopping_list_item_repository = shopping_list_item_repository

        os.environ["OPENAI_API_KEY"] = settings.AGENT_API_KEY

        self.recipe_gen_agent = Agent(
            model=settings.AGENT_MODEL,
            instructions=(
                "You are a helpful assistant specialized in recipes.\n\n"
                "Rules:\n"
                "1. Always respond in the same language as the user's query.\n"
                "2. Always use metric units (grams, milliliters, etc.) for ingredient quantities.\n"
                "3. If the user provides a recipe:\n"
                "   - Extract the recipe title.\n"
                "   - Extract the ingredients with quantities.\n"
                "4. If the user requests a recipe:\n"
                "   - Generate a recipe title.\n"
                "   - Provide a list of ingredients with metric quantities.\n"
                "5. If the user mentions an allergy:\n"
                "   - Do not include the allergen in the recipe.\n"
                "   - Add a note reminding the user to carefully review the ingredient list for allergens.\n"
                "6. If the query is unrelated to recipes (extraction or generation), do not try to invent a recipe; fail."
            ),
            model_settings=ModelSettings(
                temperature=0.0,
            ),
            output_type=PromptedOutput(
                [RecipeResponse],
                name="Recipe",
                description=(
                    "Return RecipeResponse = Recipe if the query is recipe-related. "
                    "Return RecipeResponse = InvalidRequest if the query is irrelevant."
                ),
            ),
        )

        self.recipe_merge_agent = Agent(
            model=settings.AGENT_MODEL,
            instructions=(
                "You are a helpful assistant specialized in recipes and shopping list management.\n\n"
                "Rules:\n"
                "1. Always respond in the same language as the user's query.\n"
                "2. Always use metric units (grams, milliliters, etc.) for ingredient quantities.\n"
                "3. If the user provides a recipe:\n"
                "   - Extract the recipe title.\n"
                "   - Extract the ingredients with quantities.\n"
                "4. If the user requests a recipe:\n"
                "   - Generate a recipe title.\n"
                "   - Provide a list of ingredients with metric quantities.\n"
                "5. You will receive a list of existing shopping list items using 'get_shopping_list_items' tool.\n"
                "6. Your task is to generate a recipe and compare its ingredients with the existing shopping list items.\n"
                " - If an ingredient already exists in the list and the new quantity is smaller than the current one, or if the quantity is not specified, include it in 'updated_items' with its id and new name."
                " - If an ingredient already exists in the list and is marked as purchased:\n"
                "    > If its quantity is sufficient, do not include it anywhere.\n"
                "    > If its quantity is insufficient, create a new entry with the required quantity and include it in 'new_items'.\n"
                " - If an ingredient already exists in the list and is not marked as purchased, include it in 'new_items'.\n"
                " - If an ingredient does not exist in the list, include it in 'new_items'.\n"
                " - Not include any other fields or extra information, except 'updated_items' and 'new_items'.\n"
                "7. Always return the response strictly according to the expected output type.\n"
                "8. If the user mentions an allergy:\n"
                " - Do not include the allergen in the recipe.\n"
                " - Add a note reminding the user to carefully review the ingredient list for allergens.\n"
                "9. If the query is unrelated to recipes, do not invent a recipe; instead, return the type indicating an invalid request.\n"
                "10. Do not add extra text or explanations; return only the structured response."
            ),
            model_settings=ModelSettings(
                temperature=0.0,
            ),
            tools=[Tool(self.get_shopping_list_items, takes_ctx=True)],
            output_type=PromptedOutput(
                [UpdateShoppingListWithRecipeResponse],
                name="Recipe",
                description=(
                    "Return UpdateShoppingListWithRecipeResponse = UpdateShoppingListWithRecipe if the query is recipe-related. "
                    "Return UpdateShoppingListWithRecipeResponse = InvalidRequest if the query is irrelevant."
                ),
            ),
        )

    async def get_ingredients_for_recipe(self, recipe_request: str) -> RecipeResponse:
        try:
            result = await self.recipe_gen_agent.run(recipe_request)

            return result.output
        except ModelRetry:
            raise BadGatewayException("LLM retry error")
        except Exception as exc:
            logger.error(f"Unexpected error during recipe generation: {exc}")
            raise InternalException(detail="Unexpected error during recipe generation.")

    async def get_shopping_list_items(
        self, ctx: RunContext[RecipeMergeAgentDeps]
    ) -> list[dict]:
        """Tool to fetch shopping list items based on the provided shopping_list_id."""
        items = await self.shopping_list_item_repository.get_all_by_shopping_list_id(
            str(ctx.deps.shopping_list_id)
        )

        return [
            RecipeMergeShoppingListItem(
                id=item.id, name=item.name, purchased=item.purchased
            ).model_dump()
            for item in items
        ]

    async def get_ingredients_and_merge_with_shopping_list(
        self, recipe_request: RecipeMergeRequestIn, user_id: uuid.UUID
    ) -> UpdateShoppingListWithRecipeResponse:
        await self._check_get_ingredients_permissions(
            recipe_request.shopping_list_id, user_id
        )

        try:
            result = await self.recipe_merge_agent.run(
                recipe_request.recipe_request,
                deps=RecipeMergeAgentDeps(
                    shopping_list_id=recipe_request.shopping_list_id
                ),
            )

            return result.output
        except ModelRetry:
            raise BadGatewayException("LLM retry error")
        except Exception as exc:
            logger.error(
                f"Unexpected error during recipe generation and merging: {exc}"
            )
            raise InternalException(
                detail="Unexpected error during recipe generation and merging."
            )

    async def _check_get_ingredients_permissions(
        self, shopping_list_id: uuid.UUID, user_id: uuid.UUID
    ):
        shopping_list = await self.shopping_list_repository.get_by_id(shopping_list_id)

        if not shopping_list:
            raise NotFoundException("Shopping list not found")

        is_family_member = await self.family_repository.is_member(
            shopping_list.family_id, user_id
        )
        if not is_family_member:
            raise ForbiddenException("User is not member of family")


def get_recipe_service(
    family_repository: Annotated[FamilyRepository, Depends(get_family_repository)],
    shopping_list_repository: Annotated[
        ShoppingListRepository, Depends(get_shopping_list_repository)
    ],
    shopping_list_item_repository: Annotated[
        ShoppingListItemRepository, Depends(get_shopping_list_item_repository)
    ],
) -> RecipeService:
    return RecipeService(
        family_repository=family_repository,
        shopping_list_repository=shopping_list_repository,
        shopping_list_item_repository=shopping_list_item_repository,
    )
