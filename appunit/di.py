from typing import Any, Dict, Type, TypeVar

from injector import (
    Injector,
    Provider,
    Scope,
    ScopeDecorator,
    SingletonScope,
    inject,
    singleton,
)

from appunit import ctx

__all__ = [
    "Injector",
    "Provider",
    "RequestScope",
    "Scope",
    "ScopeDecorator",
    "SingletonScope",
    "inject",
    "request",
    "singleton",
]

T = TypeVar("T")


class CachedProviderWrapper(Provider):
    def __init__(self, old_provider: Provider) -> None:
        self._old_provider = old_provider
        self._cache: Dict[int, Any] = {}

    def get(self, injector: Injector) -> Any:
        key = id(injector)
        try:
            return self._cache[key]
        except KeyError:
            instance = self._cache[key] = self._old_provider.get(injector)
            return instance


class RequestScope(Scope):
    def get(self, key: Type[T], old_provider: Provider[T]) -> Provider[T]:
        scope: dict = ctx.get_request_scope()
        try:
            return scope[key]
        except KeyError:
            new_provider = scope[key] = CachedProviderWrapper(old_provider)
            ctx.set_request_scope(scope)
            return new_provider


request = ScopeDecorator(RequestScope)
