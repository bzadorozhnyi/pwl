from datetime import datetime
from enum import StrEnum

from sqlmodel import SQLModel, Field


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


class UserDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    full_name: str = Field(nullable=False)
    password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
    role: UserRole = Field(default=UserRole.USER, nullable=False)
