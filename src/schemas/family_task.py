import uuid
from typing import Annotated

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field

from schemas.shared import AssigneeOut, CreatorOut


class CreateFamilyTaskIn(BaseModel):
    family_id: uuid.UUID
    assignee_id: uuid.UUID
    title: Annotated[str, Field(min_length=1)]


class UpdateFamilyTaskIn(BaseModel):
    assignee_id: uuid.UUID | None = None
    title: Annotated[str, Field(min_length=1)] | None = None
    done: bool | None = None


class UpdateDoneStatusFamilyTaskIn(BaseModel):
    done: bool


class FamilyTaskOut(BaseModel):
    id: uuid.UUID
    family_id: uuid.UUID
    assignee: AssigneeOut
    creator: CreatorOut
    title: str
    done: bool

    model_config = ConfigDict(from_attributes=True)
