import uuid
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class ShoppingList(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    family_id: uuid.UUID = Field(foreign_key="family.id")

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

    creator: "User" = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "foreign_keys": "ShoppingList.creator_id",
            "lazy": "selectin",
        },
    )


class ShoppingListItem(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    shopping_list_id: uuid.UUID = Field(foreign_key="shoppinglist.id")
    name: str = Field(nullable=False)
    purchased: bool = Field(default=False, nullable=False)
    creator_id: uuid.UUID = Field(foreign_key="user.id")

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
