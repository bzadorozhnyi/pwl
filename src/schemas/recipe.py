import uuid
from dataclasses import dataclass

from pydantic import BaseModel, Field


class RecipeRequestIn(BaseModel):
    recipe_request: str


class Ingredient(BaseModel):
    name: str = Field(description="Name of the ingredient with quantity")


class Recipe(BaseModel):
    title: str = Field(description="Title of the recipe")
    ingredients: list[Ingredient] = Field(description="List of ingredients")
    note: str | None = Field(default=None, description="Optional note about allergens")


class InvalidRequest(BaseModel):
    error_message: str = Field(
        description="Error message indicating why the request is invalid"
    )


RecipeResponse = Recipe | InvalidRequest


class RecipeMergeRequestIn(BaseModel):
    recipe_request: str
    shopping_list_id: uuid.UUID


class RecipeMergeShoppingListItem(BaseModel):
    id: uuid.UUID = Field(description="ID of the shopping list item")
    name: str = Field(description="Name of the shopping list item")
    purchased: bool = Field(description="Whether the item has been purchased or not")


@dataclass
class RecipeMergeAgentDeps:
    shopping_list_id: uuid.UUID


class NewItemWithRecipe(BaseModel):
    name: str = Field(description="Name of the new shopping list item")


class UpdatedItemWithRecipe(BaseModel):
    id: uuid.UUID = Field(description="ID of the shopping list item that was updated")
    name: str = Field(description="New name of the updated shopping list item")


class UpdateShoppingListWithRecipe(BaseModel):
    updated_items: list[UpdatedItemWithRecipe] = Field(
        description="Details of the updated shopping list item"
    )
    new_items: list[NewItemWithRecipe] = Field(
        description="List of new shopping list items to be added"
    )


UpdateShoppingListWithRecipeResponse = UpdateShoppingListWithRecipe | InvalidRequest
