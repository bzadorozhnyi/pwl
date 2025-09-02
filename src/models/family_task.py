import uuid
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class FamilyTask(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    family_id: uuid.UUID = Field(foreign_key="family.id")
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    assignee_id: uuid.UUID = Field(foreign_key="user.id")
    title: str = Field(nullable=False)
    done: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

    family: "Family" = Relationship(back_populates="tasks")  # noqa: F821
    creator: "User" = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "foreign_keys": "FamilyTask.creator_id",
            "lazy": "selectin",
        },
    )
    assignee: "User" = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "foreign_keys": "FamilyTask.assignee_id",
            "lazy": "selectin",
        },
    )
