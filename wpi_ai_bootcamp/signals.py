"""Signal processing helpers for WPI AI Course notebooks."""

from __future__ import annotations


def detect_r_peaks_pan_tompkins(
    ecg,
    fs: float,
    *,
    qrs_band: tuple[float, float] = (5.0, 15.0),
    filter_order: int = 2,
    integration_window_s: float = 0.150,
    threshold_scale: float = 0.25,
    refractory_s: float = 0.200,
    search_window_s: float = 0.100,
    learning_window_s: float = 2.0,
    t_wave_window_s: float = 0.360,
    searchback_factor: float = 1.66,
) -> dict[str, object]:
    """Detect ECG R-peaks using a sampling-rate adapted Pan-Tompkins pipeline.

    The decision logic follows the Pan-Tompkins QRS detector: QRS-band
    filtering, derivative, squaring, moving-window integration, adaptive signal
    and noise thresholds, T-wave rejection, and missed-beat searchback. The
    filters and windows are expressed in seconds/Hz so the helper works with the
    360 Hz SciPy ECG sample used in the course.
    """

    import numpy as np
    from scipy import signal

    values = np.asarray(ecg, dtype=float)
    if values.ndim != 1:
        raise ValueError("ecg must be a 1-D signal")
    if fs <= 0:
        raise ValueError("fs must be positive")
    if not 0 < threshold_scale < 1:
        raise ValueError("threshold_scale must be between 0 and 1")

    sos = signal.butter(filter_order, qrs_band, btype="bandpass", fs=fs, output="sos")
    bandpassed = signal.sosfiltfilt(sos, values)

    derivative = np.diff(bandpassed, prepend=bandpassed[0])
    squared = derivative**2

    integration_window = max(1, int(round(integration_window_s * fs)))
    kernel = np.ones(integration_window, dtype=float) / integration_window
    integrated = np.convolve(squared, kernel, mode="same")

    refractory = max(1, int(round(refractory_s * fs)))
    search = max(1, int(round(search_window_s * fs)))
    t_wave_window = max(refractory + 1, int(round(t_wave_window_s * fs)))

    candidate_locs, _ = signal.find_peaks(integrated, distance=refractory)
    candidate_locs = np.asarray(candidate_locs, dtype=int)

    learning_samples = min(len(values), max(refractory, int(round(learning_window_s * fs))))
    learning_integrated = integrated[:learning_samples] if learning_samples else integrated
    learning_bandpassed = np.abs(bandpassed[:learning_samples]) if learning_samples else np.abs(bandpassed)

    signal_level_i = 0.25 * float(np.max(learning_integrated)) if learning_integrated.size else 0.0
    noise_level_i = 0.50 * float(np.mean(learning_integrated)) if learning_integrated.size else 0.0
    signal_level_f = 0.25 * float(np.max(learning_bandpassed)) if learning_bandpassed.size else 0.0
    noise_level_f = 0.50 * float(np.mean(learning_bandpassed)) if learning_bandpassed.size else 0.0

    qrs_locs: list[int] = []
    qrs_integrated_peaks: list[float] = []
    rr_intervals: list[int] = []
    searchback_locs: list[int] = []
    previous_qrs_slope = 0.0

    processed_until = 0

    def thresholds() -> tuple[float, float, float, float]:
        threshold_i1 = noise_level_i + threshold_scale * (signal_level_i - noise_level_i)
        threshold_f1 = noise_level_f + threshold_scale * (signal_level_f - noise_level_f)
        return threshold_i1, 0.5 * threshold_i1, threshold_f1, 0.5 * threshold_f1

    def filtered_peak_near(candidate: int) -> tuple[int, float]:
        left = max(0, int(candidate) - search)
        right = min(len(values), int(candidate) + search + 1)
        local = left + int(np.argmax(np.abs(bandpassed[left:right])))
        return local, float(abs(bandpassed[local]))

    def integrated_slope_near(candidate: int) -> float:
        half_window = max(1, int(round(0.075 * fs)))
        left = max(0, int(candidate) - half_window)
        right = min(len(integrated), int(candidate) + 1)
        if right - left < 2:
            return 0.0
        return float(np.max(np.abs(np.diff(integrated[left:right]))))

    def accept_peak(loc: int, candidate: int, peak_i: float, peak_f: float, searchback: bool = False) -> None:
        nonlocal signal_level_i, signal_level_f, previous_qrs_slope
        if qrs_locs and loc - qrs_locs[-1] < refractory:
            if peak_f <= abs(bandpassed[qrs_locs[-1]]):
                return
            qrs_locs[-1] = loc
            qrs_integrated_peaks[-1] = peak_i
            return

        if qrs_locs:
            rr_intervals.append(loc - qrs_locs[-1])
        qrs_locs.append(loc)
        qrs_integrated_peaks.append(peak_i)
        signal_level_i = 0.125 * peak_i + 0.875 * signal_level_i
        signal_level_f = 0.125 * peak_f + 0.875 * signal_level_f
        previous_qrs_slope = integrated_slope_near(candidate)
        if searchback:
            searchback_locs.append(loc)

    def mark_noise(peak_i: float, peak_f: float) -> None:
        nonlocal noise_level_i, noise_level_f
        noise_level_i = 0.125 * peak_i + 0.875 * noise_level_i
        noise_level_f = 0.125 * peak_f + 0.875 * noise_level_f

    for idx, candidate in enumerate(candidate_locs):
        processed_until = idx
        peak_i = float(integrated[candidate])
        filtered_loc, peak_f = filtered_peak_near(int(candidate))
        threshold_i1, threshold_i2, threshold_f1, threshold_f2 = thresholds()

        if qrs_locs and rr_intervals:
            recent_rr = rr_intervals[-8:]
            rr_average = float(np.mean(recent_rr))
            rr_missed_limit = searchback_factor * rr_average
            if candidate - qrs_locs[-1] > rr_missed_limit:
                search_left = qrs_locs[-1] + refractory
                search_right = int(candidate) - refractory
                missed = [
                    int(loc)
                    for loc in candidate_locs[:idx]
                    if search_left <= int(loc) <= search_right
                ]
                if missed:
                    missed_peaks = np.asarray([integrated[loc] for loc in missed], dtype=float)
                    best_candidate = missed[int(np.argmax(missed_peaks))]
                    best_i = float(integrated[best_candidate])
                    best_loc, best_f = filtered_peak_near(best_candidate)
                    if best_i >= threshold_i2 and best_f >= threshold_f2:
                        accept_peak(best_loc, best_candidate, best_i, best_f, searchback=True)

        is_qrs = peak_i >= threshold_i1 and peak_f >= threshold_f1
        if is_qrs and qrs_locs and filtered_loc - qrs_locs[-1] < t_wave_window:
            current_slope = integrated_slope_near(int(candidate))
            if previous_qrs_slope > 0 and current_slope < 0.5 * previous_qrs_slope:
                is_qrs = False

        if is_qrs:
            accept_peak(filtered_loc, int(candidate), peak_i, peak_f)
        else:
            mark_noise(peak_i, peak_f)

    # If the final accepted beat is followed by a long gap, perform one final
    # low-threshold search over unaccepted candidates near the tail of the trace.
    if qrs_locs and rr_intervals and processed_until < len(candidate_locs):
        threshold_i1, threshold_i2, threshold_f1, threshold_f2 = thresholds()
        rr_missed_limit = searchback_factor * float(np.mean(rr_intervals[-8:]))
        if len(values) - qrs_locs[-1] > rr_missed_limit:
            missed = [
                int(loc)
                for loc in candidate_locs[processed_until:]
                if int(loc) > qrs_locs[-1] + refractory
            ]
            if missed:
                missed_peaks = np.asarray([integrated[loc] for loc in missed], dtype=float)
                best_candidate = missed[int(np.argmax(missed_peaks))]
                best_i = float(integrated[best_candidate])
                best_loc, best_f = filtered_peak_near(best_candidate)
                if best_i >= threshold_i2 and best_f >= threshold_f2:
                    accept_peak(best_loc, best_candidate, best_i, best_f, searchback=True)

    r_locs = np.asarray(sorted(set(qrs_locs)), dtype=int)
    r_times = r_locs / float(fs)

    if len(r_times) >= 2:
        rr = np.diff(r_times)
        hr = 60.0 / rr
        hr_t = r_times[1:]
    else:
        hr = np.asarray([], dtype=float)
        hr_t = np.asarray([], dtype=float)

    threshold_i1, threshold_i2, threshold_f1, threshold_f2 = thresholds()

    return {
        "r_locs": r_locs,
        "r_times": r_times,
        "hr": hr,
        "hr_t": hr_t,
        "bandpassed": bandpassed,
        "derivative": derivative,
        "squared": squared,
        "integrated": integrated,
        "threshold": float(threshold_i1),
        "threshold_i1": float(threshold_i1),
        "threshold_i2": float(threshold_i2),
        "threshold_f1": float(threshold_f1),
        "threshold_f2": float(threshold_f2),
        "signal_level_i": float(signal_level_i),
        "noise_level_i": float(noise_level_i),
        "signal_level_f": float(signal_level_f),
        "noise_level_f": float(noise_level_f),
        "candidate_locs": candidate_locs,
        "searchback_locs": np.asarray(sorted(set(searchback_locs)), dtype=int),
    }


def estimate_qrs_widths(
    ecg,
    r_locs,
    fs: float,
    *,
    search_window_s: float = 0.180,
    relative_height: float = 0.50,
) -> dict[str, object]:
    """Estimate QRS widths around detected R-peaks.

    Width is measured on the absolute ECG amplitude around each R-peak at a
    relative height of the local peak. The result is a simple lab feature for
    comparing narrow and wide synthetic complexes, not a clinical measurement.
    """

    import numpy as np

    values = np.asarray(ecg, dtype=float)
    peaks = np.asarray(r_locs, dtype=int)
    if values.ndim != 1:
        raise ValueError("ecg must be a 1-D signal")
    if fs <= 0:
        raise ValueError("fs must be positive")
    if not 0 < relative_height < 1:
        raise ValueError("relative_height must be between 0 and 1")

    search = max(1, int(round(search_window_s * fs)))
    width_samples = np.full(len(peaks), np.nan, dtype=float)
    left_locs = np.full(len(peaks), -1, dtype=int)
    right_locs = np.full(len(peaks), -1, dtype=int)

    abs_values = np.abs(values)
    for i, loc in enumerate(peaks):
        if loc < 0 or loc >= len(values):
            continue
        left = max(0, int(loc) - search)
        right = min(len(values), int(loc) + search + 1)
        local_peak = left + int(np.argmax(abs_values[left:right]))
        amplitude = abs_values[local_peak]
        if amplitude <= 0:
            continue

        threshold = relative_height * amplitude
        left_edge = local_peak
        while left_edge > left and abs_values[left_edge] >= threshold:
            left_edge -= 1
        right_edge = local_peak
        while right_edge < right - 1 and abs_values[right_edge] >= threshold:
            right_edge += 1

        width_samples[i] = right_edge - left_edge
        left_locs[i] = left_edge
        right_locs[i] = right_edge

    return {
        "width_samples": width_samples,
        "width_s": width_samples / float(fs),
        "width_ms": 1000.0 * width_samples / float(fs),
        "left_locs": left_locs,
        "right_locs": right_locs,
    }
