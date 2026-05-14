"""Minimal registry primitives for harness components."""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar


T = TypeVar("T")


class Registry(Generic[T]):
    """Name-to-object registry with explicit duplicate protection."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._items: dict[str, T] = {}

    def register(self, key: str, item: T | None = None):
        if item is None:

            def decorator(value: T) -> T:
                self.register(key, value)
                return value

            return decorator

        if key in self._items:
            raise KeyError(f"{self.name} registry already contains {key!r}")
        self._items[key] = item
        return item

    def get(self, key: str) -> T:
        try:
            return self._items[key]
        except KeyError as exc:
            available = ", ".join(sorted(self._items)) or "<empty>"
            raise KeyError(f"{key!r} is not registered in {self.name}. Available: {available}") from exc

    def names(self) -> list[str]:
        return sorted(self._items)

    def __contains__(self, key: object) -> bool:
        return key in self._items


dataset_registry: Registry[Callable] = Registry("datasets")
model_registry: Registry[Callable] = Registry("models")
loss_registry: Registry[Callable] = Registry("losses")
metric_registry: Registry[Callable] = Registry("metrics")

