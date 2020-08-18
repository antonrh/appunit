import abc
from typing import Callable, List, Optional

from pydantic import BaseModel, Field


class Route(BaseModel):
    path: str
    route: Callable
    methods: Optional[List[str]] = None
    name: Optional[str] = None
    include_in_schema: bool = True


class RouterMixin:
    @abc.abstractmethod
    def add_route(
        self,
        path: str,
        route: Callable,
        *,
        methods: List[str] = None,
        name: str = None,
        include_in_schema: bool = True,
    ):
        ...

    def route(
        self,
        path: str,
        *,
        methods: List[str] = None,
        name: str = None,
        include_in_schema: bool = True,
    ) -> Callable:
        def decorator(route: Callable) -> Callable:
            self.add_route(
                path,
                route=route,
                methods=methods,
                name=name,
                include_in_schema=include_in_schema,
            )
            return route

        return decorator

    def get(self, path: str, *, name: Optional[str] = None, **params) -> Callable:
        return self.route(path, methods=["GET"], name=name, **params)

    def head(self, path: str, *, name: Optional[str] = None, **params) -> Callable:
        return self.route(path, methods=["HEAD"], name=name, **params)

    def post(self, path: str, *, name: Optional[str] = None, **params) -> Callable:
        return self.route(path, methods=["POST"], name=name, **params)

    def put(self, path: str, *, name: Optional[str] = None, **params) -> Callable:
        return self.route(path, methods=["PUT"], name=name, **params)

    def patch(self, path: str, *, name: Optional[str] = None, **params) -> Callable:
        return self.route(path, methods=["PATCH"], name=name, **params)

    def delete(self, path: str, *, name: Optional[str] = None, **params) -> Callable:
        return self.route(path, methods=["DELETE"], name=name, **params)

    def options(self, path: str, *, name: Optional[str] = None, **params) -> Callable:
        return self.route(path, methods=["OPTIONS"], name=name, **params)

    def trace(self, path: str, *, name: Optional[str] = None, **params) -> Callable:
        return self.route(path, methods=["TRACE"], name=name, **params)


class Router(RouterMixin, BaseModel):
    prefix: Optional[str] = None
    routes: List[Route] = Field(default_factory=list)

    def add_route(
        self,
        path: str,
        route: Callable,
        *,
        methods: List[str] = None,
        name: str = None,
        include_in_schema: bool = True,
    ):
        self.routes.append(
            Route(
                path=path,
                route=route,
                methods=methods,
                name=name,
                include_in_schema=include_in_schema,
            )
        )
