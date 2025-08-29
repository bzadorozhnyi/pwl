import uuid
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class RequestForgotPasswordIn(BaseModel):
    email: EmailStr


class UpdateForgottenPasswordIn(BaseModel):
    token: uuid.UUID
    new_password: Annotated[str, Field(min_length=8, max_length=128)]
