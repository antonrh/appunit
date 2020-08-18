from contextvars import ContextVar, Token

from starlette.requests import Request

_request_scope: ContextVar[dict] = ContextVar("request_scope")


def get_request_scope() -> dict:
    return _request_scope.get()


def set_request_scope(value: dict) -> None:
    _request_scope.set(value)


def get_current_request() -> Request:
    try:
        request_locals = _request_scope.get()
        return request_locals["self"]
    except (LookupError, AttributeError):
        raise RuntimeError("Trying to get request out of context.")


def set_current_request(request: Request) -> Token:
    return _request_scope.set({"self": request})


def reset_current_request(token: Token) -> None:
    _request_scope.reset(token)
