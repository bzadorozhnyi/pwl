import uuid
from typing import Literal

from pydantic import BaseModel

from enums.ws import WebSocketServerEvent
from schemas.family_task import FamilyTaskOut
from schemas.shopping_list import ShoppingListOut
from schemas.shopping_list_item import ShoppingListItemOut


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


class UpdateDoneStatusOut(BaseModel):
    id: uuid.UUID
    done: bool


class UpdateDoneStatusFamilyTaskEvent(BaseServerWebSocketEvent):
    event_type: Literal[WebSocketServerEvent.USER_UPDATED_TASK_DONE_STATUS] = (
        WebSocketServerEvent.USER_UPDATED_TASK_DONE_STATUS
    )
    data: UpdateDoneStatusOut


class DeleteFamilyTaskOut(BaseModel):
    id: uuid.UUID


class DeleteFamilyTaskEvent(BaseServerWebSocketEvent):
    event_type: Literal[WebSocketServerEvent.USER_DELETED_TASK] = (
        WebSocketServerEvent.USER_DELETED_TASK
    )
    data: DeleteFamilyTaskOut


class CreateShoppingListEvent(BaseServerWebSocketEvent):
    event_type: Literal[WebSocketServerEvent.USER_CREATED_SHOPPING_LIST] = (
        WebSocketServerEvent.USER_CREATED_SHOPPING_LIST
    )
    data: ShoppingListOut


class UpdateShoppingListEvent(BaseServerWebSocketEvent):
    event_type: Literal[WebSocketServerEvent.USER_UPDATED_SHOPPING_LIST] = (
        WebSocketServerEvent.USER_UPDATED_SHOPPING_LIST
    )
    data: ShoppingListOut


class DeleteShoppingListOut(BaseModel):
    id: uuid.UUID


class DeleteShoppingListEvent(BaseServerWebSocketEvent):
    event_type: Literal[WebSocketServerEvent.USER_DELETED_SHOPPING_LIST] = (
        WebSocketServerEvent.USER_DELETED_SHOPPING_LIST
    )
    data: DeleteShoppingListOut


class CreateShoppingListItemEvent(BaseServerWebSocketEvent):
    event_type: Literal[WebSocketServerEvent.USER_CREATED_SHOPPING_LIST_ITEM] = (
        WebSocketServerEvent.USER_CREATED_SHOPPING_LIST_ITEM
    )
    data: ShoppingListItemOut


class UpdatePurchasedStatusOut(BaseModel):
    id: uuid.UUID
    purchased: bool


class UpdatePurchasedStatusShoppingListItemEvent(BaseServerWebSocketEvent):
    event_type: Literal[
        WebSocketServerEvent.USER_UPDATED_SHOPPING_LIST_ITEM_PURCHASED_STATUS
    ] = WebSocketServerEvent.USER_UPDATED_SHOPPING_LIST_ITEM_PURCHASED_STATUS
    data: UpdatePurchasedStatusOut


ServerWebSocketEvent = (
    CreateFamilyTaskEvent
    | UpdateFamilyTaskEvent
    | UpdateDoneStatusFamilyTaskEvent
    | DeleteFamilyTaskEvent
    | CreateShoppingListEvent
    | UpdateShoppingListEvent
    | DeleteShoppingListEvent
    | CreateShoppingListItemEvent
    | UpdatePurchasedStatusShoppingListItemEvent
)
