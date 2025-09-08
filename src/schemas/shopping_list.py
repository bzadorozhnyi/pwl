import uuid
from typing import Annotated

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field

from schemas.shared import CreatorOut


class CreateShoppingListIn(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    family_id: uuid.UUID


class ShoppingListOut(CreateShoppingListIn):
    id: uuid.UUID
    creator: CreatorOut
    family_id: uuid.UUID
    name: Annotated[str, Field(min_length=1)]

    model_config = ConfigDict(from_attributes=True)
