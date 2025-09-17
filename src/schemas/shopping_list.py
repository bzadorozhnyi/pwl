import uuid
from typing import Annotated

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field

from schemas.recipe import Ingredient
from schemas.shared import CreatorOut


class CreateShoppingListIn(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    family_id: uuid.UUID


class CreateShoppingListFromIngredientsIn(BaseModel):
    title: Annotated[str, Field(min_length=1)]
    ingredients: list[Ingredient]
    family_id: uuid.UUID


class UpdateShoppingListIn(BaseModel):
    name: Annotated[str, Field(min_length=1)]


class ShoppingListOut(BaseModel):
    id: uuid.UUID
    creator: CreatorOut
    family_id: uuid.UUID
    name: Annotated[str, Field(min_length=1)]

    model_config = ConfigDict(from_attributes=True)
