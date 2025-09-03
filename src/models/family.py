import uuid
from enum import StrEnum

from sqlmodel import Field, Relationship, SQLModel


class FamilyRole(StrEnum):
    ADMIN = "admin"
    MEMBER = "member"


class Family(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    members: list["FamilyMember"] = Relationship(back_populates="family")
    tasks: list["FamilyTask"] = Relationship(back_populates="family")  # noqa: F821


class FamilyMember(SQLModel, table=True):
    family_id: uuid.UUID = Field(foreign_key="family.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    role: FamilyRole = Field(default=FamilyRole.MEMBER, nullable=False)

    family: Family = Relationship(back_populates="members")
    user: "User" = Relationship(back_populates="families")  # noqa: F821
