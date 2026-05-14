"""Shared registries."""

from .core import Registry, dataset_registry, loss_registry, metric_registry, model_registry

__all__ = [
    "Registry",
    "dataset_registry",
    "loss_registry",
    "metric_registry",
    "model_registry",
]

