from typing import Optional

from fastapi import WebSocket

from ws.group_manager.base import WebSocketGroupManager


class InMemoryWebSocketGroupManager(WebSocketGroupManager[WebSocket]):
    _instance: Optional["InMemoryWebSocketGroupManager"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._local_groups: dict[str, list[WebSocket]] = {}
        self._initialized = True

    async def group_add(self, group: str, connection: WebSocket):
        await connection.accept()
        if group not in self._local_groups:
            self._local_groups[group] = []
        self._local_groups[group].append(connection)

    async def group_discard(self, group: str, connection: WebSocket):
        if group in self._local_groups:
            self._local_groups[group].remove(connection)
            if not self._local_groups[group]:
                del self._local_groups[group]

    async def group_send(self, group: str, message: dict):
        if group not in self._local_groups:
            return

        for connection in self._local_groups[group]:
            try:
                await connection.send_json(message)
            except Exception:
                await self.group_discard(group, connection)
