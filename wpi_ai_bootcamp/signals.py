"""Signal processing helpers for WPI AI Course notebooks."""

from __future__ import annotations


def detect_r_peaks_pan_tompkins(
    ecg,
    fs: float,
    *,
    qrs_band: tuple[float, float] = (5.0, 15.0),
    filter_order: int = 2,
    integration_window_s: float = 0.150,
    threshold_scale: float = 0.20,
    refractory_s: float = 0.200,
    search_window_s: float = 0.100,
) -> dict[str, object]:
    """Detect ECG R-peaks with a Pan-Tompkins style teaching pipeline.

    This is an educational implementation of the classic signal-processing
    pattern: QRS bandpass, derivative, squaring, moving-window integration,
    adaptive thresholding, and local peak refinement. It is not a clinical
    detector.
    """

    import numpy as np
    from scipy import signal

    values = np.asarray(ecg, dtype=float)
    if values.ndim != 1:
        raise ValueError("ecg must be a 1-D signal")
    if fs <= 0:
        raise ValueError("fs must be positive")

    sos = signal.butter(filter_order, qrs_band, btype="bandpass", fs=fs, output="sos")
    bandpassed = signal.sosfiltfilt(sos, values)

    derivative = np.diff(bandpassed, prepend=bandpassed[0])
    squared = derivative**2

    integration_window = max(1, int(round(integration_window_s * fs)))
    kernel = np.ones(integration_window, dtype=float) / integration_window
    integrated = np.convolve(squared, kernel, mode="same")

    noise_level = float(np.percentile(integrated, 50))
    signal_level = float(np.percentile(integrated, 95))
    threshold = noise_level + threshold_scale * (signal_level - noise_level)

    refractory = max(1, int(round(refractory_s * fs)))
    candidate_locs, _ = signal.find_peaks(
        integrated,
        distance=refractory,
        height=threshold,
    )

    search = max(1, int(round(search_window_s * fs)))
    refined: list[int] = []
    for candidate in candidate_locs:
        left = max(0, int(candidate) - search)
        right = min(len(values), int(candidate) + search + 1)
        local = left + int(np.argmax(np.abs(bandpassed[left:right])))

        if refined and local - refined[-1] < refractory:
            if abs(bandpassed[local]) > abs(bandpassed[refined[-1]]):
                refined[-1] = local
        else:
            refined.append(local)

    r_locs = np.asarray(sorted(set(refined)), dtype=int)
    r_times = r_locs / float(fs)

    if len(r_times) >= 2:
        rr = np.diff(r_times)
        hr = 60.0 / rr
        hr_t = r_times[1:]
    else:
        hr = np.asarray([], dtype=float)
        hr_t = np.asarray([], dtype=float)

    return {
        "r_locs": r_locs,
        "r_times": r_times,
        "hr": hr,
        "hr_t": hr_t,
        "bandpassed": bandpassed,
        "derivative": derivative,
        "squared": squared,
        "integrated": integrated,
        "threshold": float(threshold),
    }
