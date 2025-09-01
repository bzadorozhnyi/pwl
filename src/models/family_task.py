import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class FamilyTask(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    family_id: uuid.UUID = Field(foreign_key="family.id")
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    assignee_id: uuid.UUID = Field(foreign_key="user.id")
    title: str = Field(nullable=False)
    done: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
