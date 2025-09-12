import uuid
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class ShoppingListItem(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    shopping_list_id: uuid.UUID = Field(
        foreign_key="shoppinglist.id", ondelete="CASCADE"
    )
    name: str = Field(nullable=False)
    purchased: bool = Field(default=False, nullable=False)
    creator_id: uuid.UUID = Field(foreign_key="user.id")

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

    creator: "User" = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "foreign_keys": "ShoppingListItem.creator_id",
            "lazy": "selectin",
        },
    )

    shopping_list: "ShoppingList" = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "foreign_keys": "ShoppingListItem.shopping_list_id",
            "lazy": "selectin",
        },
    )
