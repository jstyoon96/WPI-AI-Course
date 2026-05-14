"""Exploratory BSPM reconstruction metrics for candidate-node selection."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

from examples.bspm.bspm_harness.data.bspm_superfile import SuperfileRecord


DEFAULT_SEGMENT_WEIGHTS = {
    "qrs": 0.45,
    "stt": 0.25,
    "p": 0.15,
    "all": 0.15,
}
SEGMENTS = ("all", "p", "qrs", "stt")
EPSILON = 1e-12


@dataclass(frozen=True)
class SegmentMasks:
    all: list[bool]
    p: list[bool]
    qrs: list[bool]
    stt: list[bool]
    p_fiducial_valid: bool

    def as_dict(self) -> dict[str, list[bool]]:
        return {"all": self.all, "p": self.p, "qrs": self.qrs, "stt": self.stt}


def build_segment_masks(record: SuperfileRecord) -> SegmentMasks:
    """Build P/QRS/ST-T masks from Superfile fiducials and row flags."""

    sample_times = [
        (sample_number - 1) * record.header.sampling_interval_ms for sample_number in record.sample_numbers
    ]
    p_valid = record.header.p_onset_ms >= 0 and record.header.p_offset_ms >= record.header.p_onset_ms
    qrs_valid = record.header.qrs_onset_ms >= 0 and record.header.qrs_offset_ms >= record.header.qrs_onset_ms
    t_valid = record.header.t_offset_ms >= record.header.qrs_offset_ms >= 0

    p_mask: list[bool] = []
    qrs_mask: list[bool] = []
    stt_mask: list[bool] = []

    for time_ms, flags in zip(sample_times, record.flags):
        p_flag, _pt_flag, qrs_flag, qt_flag, jt_flag = flags
        in_p = p_valid and (p_flag == 1 or record.header.p_onset_ms <= time_ms <= record.header.p_offset_ms)
        in_qrs = qrs_valid and (
            qrs_flag == 1 or record.header.qrs_onset_ms <= time_ms <= record.header.qrs_offset_ms
        )
        in_stt = t_valid and not in_qrs and (
            qt_flag == 1 or jt_flag == 1 or record.header.qrs_offset_ms < time_ms <= record.header.t_offset_ms
        )
        p_mask.append(in_p)
        qrs_mask.append(in_qrs)
        stt_mask.append(in_stt)

    return SegmentMasks(
        all=[True] * record.sample_count,
        p=p_mask,
        qrs=qrs_mask,
        stt=stt_mask,
        p_fiducial_valid=p_valid,
    )


def valid_rows_without_sentinel(
    target: list[list[float]],
    prediction: list[list[float]] | None = None,
    sentinel_values: Iterable[float] = (9999.0, -9999.0),
) -> list[bool]:
    """Return rows without sentinel values in target or prediction matrices."""

    sentinels = set(sentinel_values)
    masks: list[bool] = []
    for row_index, target_row in enumerate(target):
        pred_row = prediction[row_index] if prediction is not None else []
        masks.append(not any(value in sentinels for value in [*target_row, *pred_row]))
    return masks


def compute_candidate_metrics(
    target: list[list[float]],
    prediction: list[list[float]],
    segment_masks: SegmentMasks | dict[str, list[bool]],
    target_node_numbers: list[int] | None = None,
    segment_weights: dict[str, float] | None = None,
    valid_row_mask: list[bool] | None = None,
) -> dict[str, object]:
    """Compute exploratory ranking, segment, and per-node metrics."""

    _validate_matrix_pair(target, prediction)
    row_count = len(target)
    valid_rows = valid_row_mask if valid_row_mask is not None else [True] * row_count
    if len(valid_rows) != row_count:
        raise ValueError(f"valid_row_mask length {len(valid_rows)} does not match row count {row_count}")

    masks = segment_masks.as_dict() if isinstance(segment_masks, SegmentMasks) else segment_masks
    _validate_segment_masks(masks, row_count)

    weights = segment_weights or DEFAULT_SEGMENT_WEIGHTS
    segment_rows = [
        _segment_metric_row(segment, target, prediction, _and_masks(masks[segment], valid_rows))
        for segment in SEGMENTS
    ]
    segment_by_name = {str(row["segment"]): row for row in segment_rows}
    score = segment_balanced_nrmse_score(segment_by_name, weights)
    per_node_rows = _per_node_metric_rows(target, prediction, valid_rows, target_node_numbers)

    summary = {
        "score": score,
        "segment_balanced_nRMSE": score,
        "all_nRMSE": segment_by_name["all"]["nRMSE"],
        "p_nRMSE": segment_by_name["p"]["nRMSE"],
        "qrs_nRMSE": segment_by_name["qrs"]["nRMSE"],
        "stt_nRMSE": segment_by_name["stt"]["nRMSE"],
        "spatial_rms_error_uV": segment_by_name["all"]["spatial_rms_error_uV"],
        "frame_spatial_corr": segment_by_name["all"]["frame_spatial_corr"],
        "valid_sample_count": sum(valid_rows),
        "dropped_sentinel_sample_count": row_count - sum(valid_rows),
    }

    return {
        "summary": summary,
        "segment_metrics": segment_rows,
        "per_node_metrics": per_node_rows,
    }


def segment_balanced_nrmse_score(
    segment_metrics: dict[str, dict[str, object]], weights: dict[str, float] | None = None
) -> float | None:
    """Weighted nRMSE score, re-normalized over segments with finite values."""

    active_weights = weights or DEFAULT_SEGMENT_WEIGHTS
    weighted_sum = 0.0
    weight_sum = 0.0
    for segment, weight in active_weights.items():
        value = segment_metrics.get(segment, {}).get("nRMSE")
        if isinstance(value, (float, int)) and math.isfinite(value):
            weighted_sum += float(value) * weight
            weight_sum += weight
    return weighted_sum / weight_sum if weight_sum else None


def selected_node_rows(selected_node_numbers: list[int], node_120_numbers: list[int]) -> list[dict[str, int]]:
    """Return CSV-ready rows describing a selected sparse-node set."""

    node_120_positions = {node_number: index for index, node_number in enumerate(node_120_numbers)}
    rows: list[dict[str, int]] = []
    for order, node_number in enumerate(selected_node_numbers, start=1):
        if node_number not in node_120_positions:
            raise ValueError(f"selected node {node_number} is not in the node_120 universe")
        rows.append(
            {
                "selection_order": order,
                "node_number": node_number,
                "node_1based": node_number + 1,
                "node_120_position": node_120_positions[node_number],
            }
        )
    return rows


def _segment_metric_row(
    segment: str,
    target: list[list[float]],
    prediction: list[list[float]],
    mask: list[bool],
) -> dict[str, object]:
    selected = [index for index, include in enumerate(mask) if include]
    if not selected:
        return {
            "segment": segment,
            "sample_count": 0,
            "rmse_uV": None,
            "target_rms_uV": None,
            "nRMSE": None,
            "spatial_rms_error_uV": None,
            "frame_spatial_corr": None,
        }

    error_squares = 0.0
    target_squares = 0.0
    value_count = 0
    frame_rms_values: list[float] = []
    frame_corr_values: list[float] = []

    for index in selected:
        target_row = target[index]
        prediction_row = prediction[index]
        row_error_squares = [(predicted - observed) ** 2 for observed, predicted in zip(target_row, prediction_row)]
        error_squares += sum(row_error_squares)
        target_squares += sum(observed**2 for observed in target_row)
        value_count += len(target_row)
        frame_rms_values.append(math.sqrt(sum(row_error_squares) / len(row_error_squares)))
        corr = _pearson_corr(target_row, prediction_row)
        if corr is not None:
            frame_corr_values.append(corr)

    rmse = math.sqrt(error_squares / value_count)
    target_rms = math.sqrt(target_squares / value_count)
    return {
        "segment": segment,
        "sample_count": len(selected),
        "rmse_uV": rmse,
        "target_rms_uV": target_rms,
        "nRMSE": rmse / max(target_rms, EPSILON),
        "spatial_rms_error_uV": sum(frame_rms_values) / len(frame_rms_values),
        "frame_spatial_corr": sum(frame_corr_values) / len(frame_corr_values) if frame_corr_values else None,
    }


def _per_node_metric_rows(
    target: list[list[float]],
    prediction: list[list[float]],
    valid_row_mask: list[bool],
    target_node_numbers: list[int] | None,
) -> list[dict[str, object]]:
    node_count = len(target[0]) if target else 0
    node_numbers = target_node_numbers or list(range(node_count))
    if len(node_numbers) != node_count:
        raise ValueError(f"target_node_numbers length {len(node_numbers)} does not match node count {node_count}")

    rows: list[dict[str, object]] = []
    valid_indices = [index for index, include in enumerate(valid_row_mask) if include]
    for node_position, node_number in enumerate(node_numbers):
        observed = [target[index][node_position] for index in valid_indices]
        predicted = [prediction[index][node_position] for index in valid_indices]
        if not observed:
            rmse = target_rms = nrmse = corr = None
        else:
            rmse = math.sqrt(sum((pred - obs) ** 2 for obs, pred in zip(observed, predicted)) / len(observed))
            target_rms = math.sqrt(sum(obs**2 for obs in observed) / len(observed))
            nrmse = rmse / max(target_rms, EPSILON)
            corr = _pearson_corr(observed, predicted)
        rows.append(
            {
                "target_node_position": node_position,
                "target_node_number": node_number,
                "target_node_1based": node_number + 1,
                "sample_count": len(observed),
                "rmse_uV": rmse,
                "target_rms_uV": target_rms,
                "nRMSE": nrmse,
                "correlation": corr,
            }
        )
    return rows


def _pearson_corr(observed: list[float], predicted: list[float]) -> float | None:
    if len(observed) != len(predicted):
        raise ValueError("correlation inputs must have equal length")
    if not observed:
        return None

    observed_mean = sum(observed) / len(observed)
    predicted_mean = sum(predicted) / len(predicted)
    observed_centered = [value - observed_mean for value in observed]
    predicted_centered = [value - predicted_mean for value in predicted]
    denominator = math.sqrt(sum(value**2 for value in observed_centered)) * math.sqrt(
        sum(value**2 for value in predicted_centered)
    )
    if denominator <= EPSILON:
        return None
    return sum(obs * pred for obs, pred in zip(observed_centered, predicted_centered)) / denominator


def _and_masks(first: list[bool], second: list[bool]) -> list[bool]:
    if len(first) != len(second):
        raise ValueError(f"mask lengths differ: {len(first)} vs {len(second)}")
    return [left and right for left, right in zip(first, second)]


def _validate_matrix_pair(target: list[list[float]], prediction: list[list[float]]) -> None:
    if len(target) != len(prediction):
        raise ValueError(f"target rows {len(target)} do not match prediction rows {len(prediction)}")
    if not target:
        raise ValueError("target and prediction matrices must not be empty")
    node_count = len(target[0])
    if node_count == 0:
        raise ValueError("target and prediction matrices must have at least one node column")
    for index, (target_row, prediction_row) in enumerate(zip(target, prediction)):
        if len(target_row) != node_count or len(prediction_row) != node_count:
            raise ValueError(f"row {index}: matrix rows must have a stable node count")


def _validate_segment_masks(masks: dict[str, list[bool]], row_count: int) -> None:
    missing = [segment for segment in SEGMENTS if segment not in masks]
    if missing:
        raise ValueError(f"missing segment masks: {missing}")
    for segment in SEGMENTS:
        if len(masks[segment]) != row_count:
            raise ValueError(f"{segment} mask length {len(masks[segment])} does not match row count {row_count}")
