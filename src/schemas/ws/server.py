import uuid
from typing import Literal

from pydantic import BaseModel

from enums.ws import WebSocketServerEvent
from schemas.family_task import FamilyTaskOut


class BaseServerWebSocketEvent(BaseModel):
    family_id: uuid.UUID
    event_type: WebSocketServerEvent


class CreateFamilyTaskEvent(BaseServerWebSocketEvent):
    event_type: Literal[WebSocketServerEvent.USER_CREATED_TASK] = (
        WebSocketServerEvent.USER_CREATED_TASK
    )
    data: FamilyTaskOut


class UpdateFamilyTaskEvent(BaseServerWebSocketEvent):
    event_type: Literal[WebSocketServerEvent.USER_UPDATED_TASK] = (
        WebSocketServerEvent.USER_UPDATED_TASK
    )
    data: FamilyTaskOut


ServerWebSocketEvent = CreateFamilyTaskEvent | UpdateFamilyTaskEvent
