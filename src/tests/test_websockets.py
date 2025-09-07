import pytest
from fastapi import status
from httpx_ws import WebSocketDisconnect, aconnect_ws


@pytest.mark.anyio
async def test_websocket_connection_authentication_required(async_client):
    """Test WebSocket connection requires authentication."""
    with pytest.raises(WebSocketDisconnect) as exc_info:
        async with aconnect_ws("/api/ws/", async_client):
            pass

    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION
