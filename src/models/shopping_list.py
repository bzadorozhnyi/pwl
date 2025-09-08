import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class ShoppingList(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    family_id: uuid.UUID = Field(foreign_key="family.id")

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)


class ShoppingListItem(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    shopping_list_id: uuid.UUID = Field(foreign_key="shoppinglist.id")
    name: str = Field(nullable=False)
    purchased: bool = Field(default=False, nullable=False)
    creator_id: uuid.UUID = Field(foreign_key="user.id")

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
