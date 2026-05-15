"""Signal data loaders for WPI AI Bootcamp notebooks."""

from __future__ import annotations

from .sources import describe_source


def load_ecg_signal():
    """Load a public ECG sample for Colab notebooks.

    Returns
    -------
    tuple
        ``(ecg, fs, source)`` where ``ecg`` is a NumPy array, ``fs`` is the
        sampling rate in Hz, and ``source`` contains citation metadata.
    """

    from scipy import datasets

    ecg = datasets.electrocardiogram()
    fs = 360
    return ecg, fs, describe_source("ecg_scipy")
