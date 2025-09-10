from enum import StrEnum


class WebSocketServerEvent(StrEnum):
    USER_CREATED_TASK = "user_created_task"
    USER_UPDATED_TASK = "user_updated_task"
    USER_UPDATED_TASK_DONE_STATUS = "user_updated_task_done_status"
    USER_DELETED_TASK = "user_deleted_task"

    USER_CREATED_SHOPPING_LIST = "user_created_shopping_list"
    USER_UPDATED_SHOPPING_LIST = "user_updated_shopping_list"
    USER_DELETED_SHOPPING_LIST = "user_deleted_shopping_list"

    USER_CREATED_SHOPPING_LIST_ITEM = "user_created_shopping_list_item"
