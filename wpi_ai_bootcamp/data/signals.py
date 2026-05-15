"""Signal data loaders for WPI AI Bootcamp notebooks."""

from __future__ import annotations

from typing import Any

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


def make_ecg_mask_dataset(
    window_s: float = 2.0,
    stride_s: float = 0.5,
    mask_radius_s: float = 0.06,
    max_windows: int | None = 128,
    normalize: bool = True,
    random_state: int = 42,
) -> tuple[Any, Any, dict[str, Any]]:
    """Create a small ECG window dataset with R-peak mask labels.

    The helper uses the public SciPy ECG sample and derives teaching masks from
    a simple signal-processing detector. It is designed for Colab labs that need
    a compact segmentation-style dataset without committing raw data files.
    """

    import numpy as np
    from scipy import signal

    if window_s <= 0:
        raise ValueError("window_s must be positive")
    if stride_s <= 0:
        raise ValueError("stride_s must be positive")
    if mask_radius_s <= 0:
        raise ValueError("mask_radius_s must be positive")
    if max_windows is not None and max_windows <= 0:
        raise ValueError("max_windows must be positive or None")

    ecg, fs, source = load_ecg_signal()
    ecg = np.asarray(ecg, dtype=np.float32)

    source_window_start_s = 180.0
    source_window_duration_s = 160.0
    source_start = int(round(source_window_start_s * fs))
    source_stop = min(len(ecg), source_start + int(round(source_window_duration_s * fs)))
    segment = ecg[source_start:source_stop]

    centered = segment - float(np.median(segment))
    scale = float(np.percentile(np.abs(centered), 95))
    if scale <= 0:
        scale = float(np.std(centered)) or 1.0
    normalized_segment = centered / scale

    sos = signal.butter(2, (5.0, 15.0), btype="bandpass", fs=fs, output="sos")
    qrs_band = signal.sosfiltfilt(sos, normalized_segment)
    peak_distance = max(1, int(round(0.28 * fs)))
    prominence = max(0.25, 0.35 * float(np.std(qrs_band)))
    r_locs, _ = signal.find_peaks(qrs_band, distance=peak_distance, prominence=prominence)

    full_mask = np.zeros(len(segment), dtype=np.float32)
    radius = max(1, int(round(mask_radius_s * fs)))
    for loc in r_locs:
        left = max(0, int(loc) - radius)
        right = min(len(full_mask), int(loc) + radius + 1)
        full_mask[left:right] = 1.0

    window_len = int(round(window_s * fs))
    stride_len = int(round(stride_s * fs))
    if window_len > len(segment):
        raise ValueError("window_s is longer than the available ECG segment")

    starts = np.arange(0, len(segment) - window_len + 1, stride_len, dtype=int)
    if max_windows is not None and len(starts) > max_windows:
        rng = np.random.default_rng(random_state)
        starts = np.sort(rng.choice(starts, size=max_windows, replace=False))

    windows = np.stack([segment[start : start + window_len] for start in starts]).astype(np.float32)
    masks = np.stack([full_mask[start : start + window_len] for start in starts]).astype(np.float32)

    if normalize:
        medians = np.median(windows, axis=1, keepdims=True)
        centered_windows = windows - medians
        scales = np.percentile(np.abs(centered_windows), 95, axis=1, keepdims=True)
        scales = np.where(scales <= 0, 1.0, scales)
        windows = centered_windows / scales

    X = windows[:, np.newaxis, :].astype(np.float32)
    y_mask = masks.astype(np.float32)
    metadata = {
        "fs": fs,
        "source": source,
        "window_s": float(window_s),
        "stride_s": float(stride_s),
        "mask_radius_s": float(mask_radius_s),
        "source_window_start_s": source_window_start_s,
        "source_window_duration_s": (source_stop - source_start) / float(fs),
        "start_samples": starts + source_start,
        "r_peak_locs": r_locs + source_start,
    }
    return X, y_mask, metadata
