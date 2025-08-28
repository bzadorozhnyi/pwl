import uuid
from enum import StrEnum

from sqlmodel import Field, Relationship, SQLModel


class FamilyRole(StrEnum):
    ADMIN = "admin"
    MEMBER = "member"


class Family(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    role: FamilyRole = Field(default=FamilyRole.MEMBER, nullable=False)

    users: list["User"] = Relationship(back_populates="family")  # noqa: F821

