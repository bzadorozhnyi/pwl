from datetime import datetime, timezone
from typing import Callable

from fastapi import Request, Response

from core.logging import logger


async def log_requests(
    request: Request, call_next: Callable[[Request], Response]
) -> Response:
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
    with logger.contextualize(
        request=request.method, url=str(request.url), timestamp=timestamp
    ):
        response = await call_next(request)
    return response
