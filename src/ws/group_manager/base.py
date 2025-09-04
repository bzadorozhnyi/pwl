from abc import ABC, abstractmethod
from typing import Generic, TypeVar

C = TypeVar("C")


class WebSocketGroupManager(ABC, Generic[C]):
    @abstractmethod
    async def group_add(self, group: str, connection: C):
        pass

    @abstractmethod
    async def group_discard(self, group: str, connection: C):
        pass

    @abstractmethod
    async def group_send(self, group: str, message: str):
        pass
