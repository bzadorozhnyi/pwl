import uuid

from pydantic import BaseModel


class CreateFamilyTaskIn(BaseModel):
    family_id: uuid.UUID
    assignee_id: uuid.UUID
    title: str


class FamilyTaskOut(BaseModel):
    id: uuid.UUID
    family_id: uuid.UUID
    assignee_id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    done: bool
