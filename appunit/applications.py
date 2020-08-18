import asyncio
import functools
import inspect
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    cast,
)

import click
from injector import (
    Binder,
    Injector,
    Module as _Module,
    Scope,
    ScopeDecorator,
    SingletonScope,
    inject,
)
from starlette.exceptions import ExceptionMiddleware
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Router
from starlette.types import ASGIApp, Receive, Scope as ASGIScope, Send

from appunit.routing import RouterMixin

try:
    import uvicorn
except ImportError:
    uvicorn = None

from appunit import context
from appunit.middleware import RequestScopeMiddleware

Interface = TypeVar("Interface")
ScopeType = Union[Type[Scope], ScopeDecorator]
ModuleType = Union[Type["Module"], "Module"]


class AppUnit(RouterMixin):
    def __init__(
        self,
        debug: bool = False,
        exception_handlers: Dict[Union[int, Type[Exception]], Callable] = None,
        middleware: Sequence[Union[Middleware, Callable]] = None,
        response_class: Optional[Type[Response]] = None,
        modules: Optional[List[ModuleType]] = None,
        auto_bind: bool = False,
    ):
        self._debug = debug
        self.injector = Injector(auto_bind=auto_bind)
        self.router = Router()
        self.exception_handlers = {
            exc_type: handler
            for exc_type, handler in (
                {} if exception_handlers is None else dict(exception_handlers)
            ).items()
        }
        self.user_middleware = (
            []
            if middleware is None
            else [self.prepare_middleware(m) for m in middleware]
        )
        self.user_middleware.insert(0, Middleware(RequestScopeMiddleware))
        self.middleware_stack = self.build_middleware_stack()
        self.cli = click.Group()
        self.response_class = response_class or JSONResponse

        self.injector.binder.bind(AppUnit, to=self, scope=SingletonScope)
        self.injector.binder.bind(Injector, to=self.injector, scope=SingletonScope)
        self.injector.binder.bind(Request, to=context.get_current_request)

        modules = modules or []
        for module in modules:
            self.add_module(module)

    async def __call__(self, scope: ASGIScope, receive: Receive, send: Send) -> None:
        scope["app"] = self
        await self.middleware_stack(scope, receive, send)

    @property
    def debug(self) -> bool:
        return self._debug

    @debug.setter
    def debug(self, value: bool) -> None:
        self._debug = value
        self.middleware_stack = self.build_middleware_stack()

    def add_module(self, module: Union[Type["Module"], "Module"]) -> None:
        self.injector.binder.install(module)

    def lookup(
        self, interface: Type[Interface], *, scope: Optional[ScopeType] = None
    ) -> Interface:
        return self.injector.get(interface, scope=scope)

    def bind(
        self,
        interface: Type[Interface],
        to: Optional[Any] = None,
        *,
        scope: Optional[ScopeType] = None,
    ) -> None:
        self.injector.binder.bind(interface, to=to, scope=scope)

    def singleton(self, interface: Type[Interface], to: Optional[Any] = None) -> None:
        self.injector.binder.bind(interface, to=to, scope=SingletonScope)

    def add_startup_event(self, event: Callable) -> None:
        event = self._inject_event(event)
        self.router.on_startup.append(event)

    def add_shutdown_event(self, event: Callable) -> None:
        event = self._inject_event(event)
        self.router.on_shutdown.append(event)

    def on_startup(self) -> Callable:
        def decorator(event: Callable):
            self.add_startup_event(event)
            return event

        return decorator

    def on_shutdown(self) -> Callable:
        def decorator(event: Callable):
            self.add_shutdown_event(event)
            return event

        return decorator

    async def startup(self) -> None:
        await self.router.startup()

    async def shutdown(self) -> None:
        await self.router.shutdown()

    def add_route(
        self,
        path: str,
        route: Callable,
        methods: List[str] = None,
        name: str = None,
        include_in_schema: bool = True,
    ) -> None:
        self.router.add_route(
            path,
            endpoint=self._inject_route(route),
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
        )

    def add_exception_handler(
        self, status_or_exc: Union[int, Type[Exception]], *, handler: Callable
    ) -> None:
        self.exception_handlers[status_or_exc] = self._inject_exception_handler(
            handler=handler
        )
        self.middleware_stack = self.build_middleware_stack()

    def exception_handler(self, status_or_exc: Union[int, Type[Exception]]) -> Callable:
        def decorator(handler: Callable) -> Callable:
            self.add_exception_handler(status_or_exc, handler=handler)
            return handler

        return decorator

    def add_middleware(self, middleware: Union[Middleware, Callable]) -> None:
        self.user_middleware.insert(0, self.prepare_middleware(middleware))
        self.middleware_stack = self.build_middleware_stack()

    def middleware(self) -> Callable:
        def decorator(middleware: Callable) -> Callable:
            self.add_middleware(middleware)
            return middleware

        return decorator

    def prepare_middleware(self, middleware: Union[Middleware, Callable]) -> Middleware:
        if inspect.isfunction(middleware):
            middleware = Middleware(
                BaseHTTPMiddleware,
                dispatch=self._inject_middleware(cast(Callable, middleware)),
            )
        return cast(Middleware, middleware)

    def build_middleware_stack(self) -> ASGIApp:
        debug = self.debug
        error_handler = None
        exception_handlers = {}

        for key, value in self.exception_handlers.items():
            if key in (500, Exception):
                error_handler = value
            else:
                exception_handlers[key] = value

        middleware = (
            [Middleware(ServerErrorMiddleware, handler=error_handler, debug=debug)]
            + self.user_middleware
            + [
                Middleware(
                    ExceptionMiddleware, handlers=exception_handlers, debug=debug
                )
            ]
        )

        app = self.router
        for cls, options in reversed(middleware):
            app = cls(app=app, **options)
        return app

    def add_command(
        self,
        cmd: Callable,
        *,
        name: Optional[str] = None,
        cli: Optional[click.Group] = None,
        lifespan: bool = True,
    ) -> None:
        make_command = click.command()
        cli = cli or self.cli
        cli.add_command(
            make_command(self._inject_command(cmd, lifespan=lifespan)), name=name
        )

    def command(self, name: Optional[str] = None, *, lifespan: bool = True) -> Callable:
        def decorator(cmd: Callable) -> Callable:
            self.add_command(cmd, name=name, lifespan=lifespan)
            return cmd

        return decorator

    def run(self, **kwargs) -> None:
        """
        Run Uvicorn server.
        """
        if uvicorn is None:
            raise RuntimeError("`uvicorn` is not installed.")

        uvicorn.run(app=self, **kwargs)

    def main(self) -> int:
        """
        Start application CLI.
        """
        return self.cli.main()

    ############################################
    # Dependency Injection helpers
    ############################################

    def _inject_event(self, event: Callable) -> Callable:
        def wrapper(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapped():
                handler = self.injector.call_with_injection(inject(func))
                if inspect.iscoroutine(handler):
                    return await handler

            return wrapped

        return wrapper(event)

    def _inject_route(self, route: Callable) -> Callable:
        def wrapper(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapped(_: Request):
                response = self.injector.call_with_injection(inject(func))
                if inspect.iscoroutine(response):
                    response = await response

                if isinstance(response, Response):
                    return response
                return self.response_class(content=response)

            return wrapped

        return wrapper(route)

    def _inject_exception_handler(self, handler: Callable) -> Callable:
        def wrapper(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapped(request: Request, exc: Exception):
                return await self.injector.call_with_injection(
                    inject(func), args=(request, exc)
                )

            return wrapped

        return wrapper(handler)

    def _inject_middleware(self, middleware: Callable) -> Callable:
        def wrapper(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapped(request: Request, call_next: Callable):
                return await self.injector.call_with_injection(
                    inject(func), args=(request, call_next)
                )

            return wrapped

        return wrapper(middleware)

    def _inject_command(self, cmd: Callable, lifespan: bool = True) -> Callable:
        def wrapper(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                def run():
                    return self.injector.call_with_injection(
                        inject(func), args=args, kwargs=kwargs
                    )

                async def async_run():
                    if lifespan:
                        await self.startup()
                        try:
                            await run()
                        finally:
                            await self.shutdown()
                    else:
                        await run()

                if inspect.iscoroutinefunction(func):
                    return asyncio.run(async_run())
                return run()

            return wrapped

        return wrapper(cmd)


class Module(_Module):
    def __init__(self):
        self._app: Optional[AppUnit] = None

    @property
    def app(self) -> AppUnit:
        if not self._app:
            raise RuntimeError(f"{self.__class__.__name__} is not configured.")
        return self._app

    def configure(self, binder: Binder) -> None:
        self._app = binder.injector.get(AppUnit)

    def register(self) -> None:
        pass  # pragma: no cover
