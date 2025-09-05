import uuid
from typing import Any

from pydantic import BaseModel

from enums.ws import WebSocketClientEvent, WebSocketServerEvent


class ClientWebSocketEvent(BaseModel):
    family_id: uuid.UUID
    event_type: WebSocketClientEvent
    data: Any


class ServerWebSocketEvent(BaseModel):
    family_id: uuid.UUID
    event_type: WebSocketServerEvent
    data: Any
