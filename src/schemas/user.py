from typing import Annotated

from pydantic import BaseModel, EmailStr, Field
from sqlmodel import SQLModel


class UserIn(SQLModel):
    email: EmailStr
    full_name: Annotated[str, Field(max_length=255)]
    password: Annotated[str, Field(min_length=8, max_length=128)]


class UserOut(SQLModel):
    id: int
    email: EmailStr
    full_name: Annotated[str, Field(max_length=255)]


class UserAuthCredentialsIn(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=128)]
