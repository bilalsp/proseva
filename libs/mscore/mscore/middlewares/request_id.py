from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Receive, Scope, Send

from ..contexts import new_request_id


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID") -> None:
        """It generates a unique request ID for each HTTP request and sets it in the response headers."""
        self.app = app
        self.header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # generate a new request id
        request_id = new_request_id()

        # attach to scope for access in routes
        scope["request_id"] = request_id

        async def send_wrapper(message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append(self.header_name, request_id)
            await send(message)

        await self.app(scope, receive, send_wrapper)
