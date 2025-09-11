import uuid
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    username: str = Field(index=True, unique=True, nullable=False)
    password: str = Field(nullable=False)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

    is_admin: bool = Field(default=False, nullable=False)

    families: list["FamilyMember"] = Relationship(back_populates="user")  # noqa: F821
