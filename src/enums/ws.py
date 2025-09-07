from enum import StrEnum


class WebSocketClientEvent(StrEnum):
    CREATED_TASK = "created_task"
    UPDATED_TASK = "updated_task"


class WebSocketServerEvent(StrEnum):
    USER_CREATED_TASK = "user_created_task"
    USER_UPDATED_TASK = "user_updated_task"
    USER_UPDATED_TASK_DONE_STATUS = "user_updated_task_done_status"
    USER_DELETED_TASK = "user_deleted_task"
