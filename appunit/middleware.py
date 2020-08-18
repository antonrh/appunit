from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from appunit import ctx


class RequestScopeMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        token = ctx.set_current_request(request)
        try:
            return await call_next(request)
        finally:
            ctx.reset_current_request(token)
