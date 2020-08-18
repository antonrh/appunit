from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from appunit import context


class RequestScopeMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        token = context.set_current_request(request)
        try:
            return await call_next(request)
        finally:
            context.reset_current_request(token)
