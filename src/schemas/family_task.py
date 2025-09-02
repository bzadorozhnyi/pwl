import uuid

from pydantic import BaseModel


class CreateFamilyTaskIn(BaseModel):
    family_id: uuid.UUID
    assignee_id: uuid.UUID
    title: str


class AssigneeOut(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str


class CreatorOut(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str


class FamilyTaskOut(BaseModel):
    id: uuid.UUID
    family_id: uuid.UUID
    assignee: AssigneeOut
    creator: CreatorOut
    title: str
    done: bool
