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

    family: "Family" = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "foreign_keys": "ShoppingList.family_id",
        },
    )

    def __str__(self):
        return f"ShoppingList ({self.id})"
