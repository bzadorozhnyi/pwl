from pydantic import BaseModel, Field


class RecipeRequestIn(BaseModel):
    request: str


class Ingredient(BaseModel):
    name: str = Field(description="Name of the ingredient")
    quantity: str = Field(description="Quantity of the ingredient")


class Recipe(BaseModel):
    title: str = Field(description="Title of the recipe")
    ingredients: list[Ingredient] = Field(description="List of ingredients")
    note: str | None = Field(default=None, description="Optional note about allergens")


class InvalidRequest(BaseModel):
    error_message: str = Field(description="Error message indicating why the request is invalid")


RecipeResponse = Recipe | InvalidRequest