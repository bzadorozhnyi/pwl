from fastapi import status


class WebSocketAuthorizationCredentials:
    def __init__(self, token: str):
        self.credentials = token


class WebSocketBearer:
    async def __call__(self, websocket) -> WebSocketAuthorizationCredentials | None:
        authorization = websocket.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None

        token = authorization[7:]
        return WebSocketAuthorizationCredentials(token=token)
