from enum import StrEnum


class WebSocketClientEvent(StrEnum):
    CREATED_TASK = "created_task"
    UPDATED_TASK = "updated_task"


class WebSocketServerEvent(StrEnum):
    USER_CREATED_TASK = "user_created_task"
    USER_UPDATED_TASK = "user_updated_task"
