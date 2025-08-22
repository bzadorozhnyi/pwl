import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from core.logging import logger, request_id_var


class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        request.state.request_id = request_id
        request_id_var.set(request_id)

        platform = request.headers.get("X-Platform", "unknown")
        app_version = request.headers.get("X-App-Version", "unknown")

        request_logger = logger.bind(
            request_id=request_id,
            platform=platform,
            app_version=app_version,
        )
        method = request.method
        path = request.url.path

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as e:
            duration = time.perf_counter() - start_time
            request_logger.opt(exception=True).error(
                f"Exception during {method} {path} [{duration:.2f}s]"
            )
            raise e

        duration = time.perf_counter() - start_time
        status = response.status_code

        request_logger.info(f"{method} {path} → {status} [{duration:.2f}s]")

        response.headers[self.header_name] = request_id
        return response
