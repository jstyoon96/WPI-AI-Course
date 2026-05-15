"""Data loading helpers for WPI AI Bootcamp notebooks.

This package contains code for loading public or library-provided data. It does
not store large datasets.
"""

from .imaging import load_imaging_sample
from .signals import load_ecg_signal, make_ecg_mask_dataset
from .sources import DataSource, describe_source

__all__ = [
    "DataSource",
    "describe_source",
    "load_ecg_signal",
    "load_imaging_sample",
    "make_ecg_mask_dataset",
]
