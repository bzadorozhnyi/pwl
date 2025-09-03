import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field
from sqlmodel import SQLModel

from models.family import FamilyRole
from schemas.token import TokenPairOut


class UserIn(SQLModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=128)]
    first_name: Annotated[str, Field(min_length=1, max_length=100)]
    last_name: Annotated[str, Field(min_length=1, max_length=100)]


class UserOut(SQLModel):
    id: uuid.UUID
    email: EmailStr
    first_name: Annotated[str, Field(max_length=100)]
    last_name: Annotated[str, Field(max_length=100)]
    created_at: datetime
    updated_at: datetime


class UserWithTokensOut(SQLModel):
    user: UserOut
    tokens: TokenPairOut


class UserAuthCredentialsIn(BaseModel):
    identifier: str
    password: Annotated[str, Field(min_length=8, max_length=128)]


class FamilyInfo(BaseModel):
    id: uuid.UUID
    role: FamilyRole


class UserProfileOut(SQLModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    first_name: Annotated[str, Field(max_length=100)]
    last_name: Annotated[str, Field(max_length=100)]
    families: list[FamilyInfo]
