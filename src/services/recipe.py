import os

from pydantic_ai import Agent, ModelRetry, PromptedOutput

from core.config import settings
from exceptions import BadGatewayException, InternalException
from schemas.recipe import RecipeResponse


class RecipeService:
    def __init__(self):
        os.environ["OPENAI_API_KEY"] = settings.AGENT_API_KEY

        self.agent = Agent(
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
            output_type=PromptedOutput(
                [RecipeResponse],
                name="Recipe",
                description=(
                    "Return RecipeResponse = Recipe if the query is recipe-related. "
                    "Return RecipeResponse = InvalidRequest if the query is irrelevant."
                ),
            ),
        )

    async def get_ingredients_for_recipe(self, request: str) -> RecipeResponse:
        try:
            result = await self.agent.run(request)

            return result.output
        except ModelRetry:
            raise BadGatewayException("LLM retry error")
        except Exception as exc:
            raise InternalException(
                detail=f"Unexpected error during recipe generation: {exc}"
            )


def get_recipe_service() -> RecipeService:
    return RecipeService()
