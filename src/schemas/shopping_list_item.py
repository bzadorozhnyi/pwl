import uuid
from typing import Annotated

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field

from schemas.shared import CreatorOut


class CreateShoppingListItemIn(BaseModel):
    shopping_list_id: uuid.UUID
    name: Annotated[str, Field(min_length=1)]


class ShoppingListItemOut(BaseModel):
    id: uuid.UUID
    creator: CreatorOut
    shopping_list_id: uuid.UUID
    purchased: bool
    name: Annotated[str, Field(min_length=1)]

    model_config = ConfigDict(from_attributes=True)
