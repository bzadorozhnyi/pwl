import uuid

from pydantic import BaseModel, ConfigDict


class AssigneeOut(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)


class CreatorOut(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)
