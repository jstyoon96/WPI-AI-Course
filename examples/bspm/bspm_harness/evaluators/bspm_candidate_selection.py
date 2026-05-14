"""Candidate-node selection baselines for BSPM sparse reconstruction."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import json
import multiprocessing as mp
import os
from pathlib import Path
import random
import subprocess
import time
from typing import Sequence

import numpy as np
from scipy.linalg import qr

from examples.bspm.bspm_harness.data.bspm_superfile import (
    SuperfileRecord,
    build_sparse_reconstruction_batch,
    extract_node_matrix,
    iter_superfile_records,
    node_indices,
    parse_node_label_xlsx,
)
from examples.bspm.bspm_harness.evaluators.bspm_metrics import (
    build_segment_masks,
    compute_candidate_metrics,
    selected_node_rows,
    valid_rows_without_sentinel,
)
from harness.reports.contracts import candidate_selection_paths


SUPPORTED_METHODS = ("random", "pca_qr", "forward_greedy")
FORWARD_GREEDY_CHECKPOINT = "forward_greedy_checkpoint.json"
FORWARD_GREEDY_PROGRESS = "forward_greedy_progress.csv"
_FORWARD_WORKER_STATE: dict[str, object] = {}


@dataclass(frozen=True)
class CandidateSelectionRun:
    run_id: str
    output_root: Path
    tracked_summary: Path
    summary_rows: list[dict[str, object]]
    selected_node_rows: list[dict[str, object]]
    segment_metric_rows: list[dict[str, object]]
    per_node_metric_rows: list[dict[str, object]]
    manifest: dict[str, object]


@dataclass(frozen=True)
class _PreparedRecord:
    source_name: str
    target: np.ndarray
    valid_rows: list[bool]
    segment_masks: dict[str, list[bool]]


@dataclass(frozen=True)
class _PreparedData:
    train_records: list[_PreparedRecord]
    val_records: list[_PreparedRecord]
    node_120_numbers: list[int]
    split_manifest: dict[str, object]


@dataclass(frozen=True)
class _EvaluationMatrices:
    train_y: np.ndarray
    val_y: np.ndarray
    val_valid_rows: list[bool]
    val_segment_masks: dict[str, list[bool]]


def load_candidate_selection_inputs(
    raw_path: str | Path,
    node_label_path: str | Path,
    max_records: int | None = None,
    seed: int = 42,
    val_fraction: float = 0.2,
) -> _PreparedData:
    """Load Superfile records and prepare node_120 targets for selection."""

    labels = parse_node_label_xlsx(node_label_path)
    node_120_numbers = node_indices(labels, "node_120")
    records = list(iter_superfile_records(raw_path, max_records=max_records))
    return prepare_candidate_selection_data(records, node_120_numbers, seed=seed, val_fraction=val_fraction)


def prepare_candidate_selection_data(
    records: Sequence[SuperfileRecord],
    node_120_numbers: list[int],
    seed: int = 42,
    val_fraction: float = 0.2,
) -> _PreparedData:
    if not records:
        raise ValueError("candidate selection requires at least one Superfile record")
    if len(node_120_numbers) != 120:
        raise ValueError(f"expected 120 node_120 numbers, found {len(node_120_numbers)}")

    prepared = [_prepare_record(record, node_120_numbers) for record in records]
    train_indices, val_indices = _record_level_split(len(prepared), seed=seed, val_fraction=val_fraction)
    train_records = [prepared[index] for index in train_indices]
    val_records = [prepared[index] for index in val_indices]

    return _PreparedData(
        train_records=train_records,
        val_records=val_records,
        node_120_numbers=node_120_numbers,
        split_manifest={
            "split_policy": "exploratory_record_level_80_20",
            "seed": seed,
            "val_fraction": val_fraction,
            "train_record_count": len(train_records),
            "val_record_count": len(val_records),
            "train_sources": [record.source_name for record in train_records],
            "val_sources": [record.source_name for record in val_records],
        },
    )


def pca_qr_order(train_y: np.ndarray, max_k: int) -> list[int]:
    """Return node_120 positions selected by SVD/PCA modes and QR pivoting."""

    _validate_k(max_k, train_y.shape[1])
    centered = train_y - train_y.mean(axis=0, keepdims=True)
    _u, _s, vt = np.linalg.svd(centered, full_matrices=False)
    mode_count = min(max_k, vt.shape[0])
    modes = vt[:mode_count, :]
    _q, _r, pivots = qr(modes, pivoting=True, mode="economic")
    return [int(position) for position in pivots[:max_k]]


def random_order(node_count: int, max_k: int, seed: int) -> list[int]:
    """Return a deterministic random node_120 position order."""

    _validate_k(max_k, node_count)
    rng = random.Random(seed)
    return rng.sample(range(node_count), max_k)


def forward_greedy_order(
    train_y: np.ndarray,
    val_y: np.ndarray,
    val_segment_masks: dict[str, list[bool]],
    val_valid_rows: list[bool],
    max_k: int,
    ridge_alpha: float = 1.0,
    worker_count: int = 1,
    initial_selected: list[int] | None = None,
    step_callback=None,
    should_stop=None,
) -> list[int]:
    """Greedily add nodes that minimize validation segment-balanced nRMSE."""

    _validate_k(max_k, train_y.shape[1])
    if worker_count < 1:
        raise ValueError(f"worker_count must be positive, found {worker_count}")
    selected: list[int] = list(initial_selected or [])
    if len(set(selected)) != len(selected):
        raise ValueError("initial_selected contains duplicate node positions")
    if len(selected) > max_k:
        raise ValueError(f"initial_selected length {len(selected)} exceeds max_k {max_k}")
    remaining = set(range(train_y.shape[1]))
    remaining.difference_update(selected)

    if worker_count == 1:
        while len(selected) < max_k:
            step_start = time.monotonic()
            candidate_count = len(remaining)
            best_position, _best_score = _best_forward_candidate(
                selected=selected,
                candidates=sorted(remaining),
                train_y=train_y,
                val_y=val_y,
                val_segment_masks=val_segment_masks,
                val_valid_rows=val_valid_rows,
                ridge_alpha=ridge_alpha,
            )
            selected.append(best_position)
            remaining.remove(best_position)
            if step_callback:
                step_callback(
                    selected=list(selected),
                    best_position=best_position,
                    best_score=_best_score,
                    candidate_count=candidate_count,
                    step_seconds=time.monotonic() - step_start,
                )
            if should_stop and should_stop():
                break
        return selected

    _set_single_thread_blas_defaults()
    ctx = mp.get_context("fork") if "fork" in mp.get_all_start_methods() else mp.get_context()
    with ctx.Pool(
        processes=worker_count,
        initializer=_init_forward_worker,
        initargs=(train_y, val_y, val_segment_masks, val_valid_rows, ridge_alpha),
    ) as pool:
        while len(selected) < max_k:
            step_start = time.monotonic()
            candidate_count = len(remaining)
            tasks = [([*selected], candidate) for candidate in sorted(remaining)]
            results = pool.map(_score_forward_candidate_worker, tasks)
            best_position, _best_score = _best_score_result(results)
            selected.append(best_position)
            remaining.remove(best_position)
            if step_callback:
                step_callback(
                    selected=list(selected),
                    best_position=best_position,
                    best_score=_best_score,
                    candidate_count=candidate_count,
                    step_seconds=time.monotonic() - step_start,
                )
            if should_stop and should_stop():
                break
    return selected


def evaluate_selected_positions(
    train_y: np.ndarray,
    val_y: np.ndarray,
    selected_positions: list[int],
    val_segment_masks: dict[str, list[bool]],
    val_valid_rows: list[bool],
    target_node_numbers: list[int] | None = None,
    ridge_alpha: float = 1.0,
) -> dict[str, object]:
    """Fit ridge from selected node positions and evaluate on validation rows."""

    prediction = _ridge_predict(
        train_y[:, selected_positions],
        train_y,
        val_y[:, selected_positions],
        ridge_alpha=ridge_alpha,
    )
    return compute_candidate_metrics(
        target=val_y.tolist(),
        prediction=prediction.tolist(),
        segment_masks=val_segment_masks,
        target_node_numbers=target_node_numbers,
        valid_row_mask=val_valid_rows,
    )


def run_candidate_selection(
    records: Sequence[SuperfileRecord],
    node_120_numbers: list[int],
    run_id: str,
    k_values: list[int],
    methods: list[str],
    output_dir: str | Path = "experiments/candidate_selection_v1",
    report_dir: str | Path = "reports/candidate_selection_v1",
    seed: int = 42,
    val_fraction: float = 0.2,
    ridge_alpha: float = 1.0,
    worker_count: int = 1,
    resume: bool = False,
    max_runtime_minutes: float | None = None,
    progress_log_name: str = FORWARD_GREEDY_PROGRESS,
    config_path: str | Path | None = None,
    raw_path: str | Path | None = None,
    node_label_path: str | Path | None = None,
) -> CandidateSelectionRun:
    """Run selected candidate baselines and write the storage contract files."""

    unknown_methods = sorted(set(methods) - set(SUPPORTED_METHODS))
    if unknown_methods:
        raise ValueError(f"unsupported candidate selection methods: {unknown_methods}")
    if not k_values:
        raise ValueError("at least one k value is required")
    k_values = sorted(set(k_values))
    max_k = max(k_values)

    prepared = prepare_candidate_selection_data(records, node_120_numbers, seed=seed, val_fraction=val_fraction)
    matrices = _evaluation_matrices(prepared)
    node_count = matrices.train_y.shape[1]
    _validate_k(max_k, node_count)

    path_contract = candidate_selection_paths(run_id, output_dir=output_dir, report_dir=report_dir)
    summary_rows: list[dict[str, object]] = []
    selected_rows: list[dict[str, object]] = []
    segment_rows: list[dict[str, object]] = []
    per_node_rows: list[dict[str, object]] = []
    manifest = _manifest(
        run_id=run_id,
        config_path=config_path,
        raw_path=raw_path,
        node_label_path=node_label_path,
        methods=methods,
        k_values=k_values,
        seed=seed,
        ridge_alpha=ridge_alpha,
        worker_count=worker_count,
        resume=resume,
        max_runtime_minutes=max_runtime_minutes,
        progress_log_name=progress_log_name,
        prepared=prepared,
        matrices=matrices,
    )
    stopped_early = False

    for method in methods:
        if method == "forward_greedy":
            method_order, stopped_early = _run_forward_greedy_with_reliability(
                train_y=matrices.train_y,
                val_y=matrices.val_y,
                val_segment_masks=matrices.val_segment_masks,
                val_valid_rows=matrices.val_valid_rows,
                node_120_numbers=node_120_numbers,
                max_k=max_k,
                k_values=k_values,
                worker_count=worker_count,
                ridge_alpha=ridge_alpha,
                run_id=run_id,
                paths=path_contract,
                manifest=manifest,
                resume=resume,
                max_runtime_minutes=max_runtime_minutes,
                progress_log_name=progress_log_name,
                summary_rows=summary_rows,
                selected_rows=selected_rows,
                segment_rows=segment_rows,
                per_node_rows=per_node_rows,
            )
        else:
            method_order = _selection_order_for_method(
                method=method,
                train_y=matrices.train_y,
                val_y=matrices.val_y,
                val_segment_masks=matrices.val_segment_masks,
                val_valid_rows=matrices.val_valid_rows,
                max_k=max_k,
                seed=seed,
                ridge_alpha=ridge_alpha,
                worker_count=worker_count,
            )
        for k_value in k_values:
            if len(method_order) >= k_value:
                _append_k_metrics(
                    run_id=run_id,
                    method=method,
                    k_value=k_value,
                    selected_positions=method_order[:k_value],
                    node_120_numbers=node_120_numbers,
                    matrices=matrices,
                    ridge_alpha=ridge_alpha,
                    summary_rows=summary_rows,
                    selected_rows=selected_rows,
                    segment_rows=segment_rows,
                    per_node_rows=per_node_rows,
                )
        if stopped_early:
            break

    manifest["status"] = "stopped_early" if stopped_early else "complete"
    _write_outputs(path_contract, summary_rows, selected_rows, segment_rows, per_node_rows, manifest)

    return CandidateSelectionRun(
        run_id=run_id,
        output_root=path_contract.root,
        tracked_summary=path_contract.tracked_summary_md,
        summary_rows=summary_rows,
        selected_node_rows=selected_rows,
        segment_metric_rows=segment_rows,
        per_node_metric_rows=per_node_rows,
        manifest=manifest,
    )


def run_candidate_selection_from_paths(
    raw_path: str | Path,
    node_label_path: str | Path,
    run_id: str,
    k_values: list[int],
    methods: list[str],
    output_dir: str | Path = "experiments/candidate_selection_v1",
    report_dir: str | Path = "reports/candidate_selection_v1",
    max_records: int | None = None,
    seed: int = 42,
    val_fraction: float = 0.2,
    ridge_alpha: float = 1.0,
    worker_count: int = 1,
    resume: bool = False,
    max_runtime_minutes: float | None = None,
    progress_log_name: str = FORWARD_GREEDY_PROGRESS,
    config_path: str | Path | None = None,
) -> CandidateSelectionRun:
    labels = parse_node_label_xlsx(node_label_path)
    node_120_numbers = node_indices(labels, "node_120")
    records = list(iter_superfile_records(raw_path, max_records=max_records))
    return run_candidate_selection(
        records=records,
        node_120_numbers=node_120_numbers,
        run_id=run_id,
        k_values=k_values,
        methods=methods,
        output_dir=output_dir,
        report_dir=report_dir,
        seed=seed,
        val_fraction=val_fraction,
        ridge_alpha=ridge_alpha,
        worker_count=worker_count,
        resume=resume,
        max_runtime_minutes=max_runtime_minutes,
        progress_log_name=progress_log_name,
        config_path=config_path,
        raw_path=raw_path,
        node_label_path=node_label_path,
    )


def _run_forward_greedy_with_reliability(
    train_y: np.ndarray,
    val_y: np.ndarray,
    val_segment_masks: dict[str, list[bool]],
    val_valid_rows: list[bool],
    node_120_numbers: list[int],
    max_k: int,
    k_values: list[int],
    worker_count: int,
    ridge_alpha: float,
    run_id: str,
    paths,
    manifest: dict[str, object],
    resume: bool,
    max_runtime_minutes: float | None,
    progress_log_name: str,
    summary_rows: list[dict[str, object]],
    selected_rows: list[dict[str, object]],
    segment_rows: list[dict[str, object]],
    per_node_rows: list[dict[str, object]],
) -> tuple[list[int], bool]:
    paths.root.mkdir(parents=True, exist_ok=True)
    checkpoint_path = paths.root / FORWARD_GREEDY_CHECKPOINT
    progress_path = paths.root / progress_log_name
    started_at = time.monotonic()
    selected: list[int] = []
    progress_rows: list[dict[str, object]] = []

    if resume and checkpoint_path.exists():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        selected = [int(value) for value in checkpoint.get("selected_positions", [])]
        progress_rows = list(checkpoint.get("score_history", []))
        print(
            f"[forward_greedy] resume run_id={run_id} completed_steps={len(selected)} "
            f"checkpoint={checkpoint_path}",
            flush=True,
        )
    else:
        print(f"[forward_greedy] start run_id={run_id} max_k={max_k} workers={worker_count}", flush=True)

    for k_value in k_values:
        if len(selected) >= k_value:
            _append_k_metrics(
                run_id=run_id,
                method="forward_greedy",
                k_value=k_value,
                selected_positions=selected[:k_value],
                node_120_numbers=node_120_numbers,
                matrices=_EvaluationMatrices(train_y, val_y, val_valid_rows, val_segment_masks),
                ridge_alpha=ridge_alpha,
                summary_rows=summary_rows,
                selected_rows=selected_rows,
                segment_rows=segment_rows,
                per_node_rows=per_node_rows,
            )

    def on_step(
        selected: list[int],
        best_position: int,
        best_score: float,
        candidate_count: int,
        step_seconds: float,
    ) -> None:
        completed_step = len(selected)
        elapsed_seconds = time.monotonic() - started_at
        best_node = node_120_numbers[best_position]
        row = {
            "run_id": run_id,
            "method": "forward_greedy",
            "step": completed_step,
            "max_k": max_k,
            "candidate_count": candidate_count,
            "workers": worker_count,
            "best_node_position": best_position,
            "best_node_number": best_node,
            "best_node_1based": best_node + 1,
            "score": best_score,
            "step_seconds": step_seconds,
            "elapsed_seconds": elapsed_seconds,
            "selected_node_numbers": ";".join(str(node_120_numbers[position]) for position in selected),
            "selected_node_1based": ";".join(str(node_120_numbers[position] + 1) for position in selected),
        }
        progress_rows.append(row)
        _write_csv(progress_path, progress_rows)
        _write_forward_checkpoint(
            checkpoint_path=checkpoint_path,
            run_id=run_id,
            selected_positions=selected,
            node_120_numbers=node_120_numbers,
            score_history=progress_rows,
            max_k=max_k,
            worker_count=worker_count,
            manifest=manifest,
        )
        print(
            "[forward_greedy] "
            f"step={completed_step}/{max_k} candidates={candidate_count} workers={worker_count} "
            f"best_node={best_node + 1} score={best_score:.8g} "
            f"step_time={_format_duration(step_seconds)} elapsed={_format_duration(elapsed_seconds)}",
            flush=True,
        )

        if completed_step in k_values:
            _append_k_metrics(
                run_id=run_id,
                method="forward_greedy",
                k_value=completed_step,
                selected_positions=selected,
                node_120_numbers=node_120_numbers,
                matrices=_EvaluationMatrices(train_y, val_y, val_valid_rows, val_segment_masks),
                ridge_alpha=ridge_alpha,
                summary_rows=summary_rows,
                selected_rows=selected_rows,
                segment_rows=segment_rows,
                per_node_rows=per_node_rows,
            )
            manifest["status"] = "running"
            _write_outputs(paths, summary_rows, selected_rows, segment_rows, per_node_rows, manifest)

    def should_stop() -> bool:
        if max_runtime_minutes is None:
            return False
        return (time.monotonic() - started_at) >= max_runtime_minutes * 60

    selected = forward_greedy_order(
        train_y=train_y,
        val_y=val_y,
        val_segment_masks=val_segment_masks,
        val_valid_rows=val_valid_rows,
        max_k=max_k,
        ridge_alpha=ridge_alpha,
        worker_count=worker_count,
        initial_selected=selected,
        step_callback=on_step,
        should_stop=should_stop,
    )
    stopped_early = len(selected) < max_k
    if stopped_early:
        print(
            f"[forward_greedy] clean_stop completed_steps={len(selected)} target_steps={max_k} "
            f"checkpoint={checkpoint_path}",
            flush=True,
        )
    else:
        print(f"[forward_greedy] complete steps={len(selected)} checkpoint={checkpoint_path}", flush=True)
    return selected, stopped_early


def _append_k_metrics(
    run_id: str,
    method: str,
    k_value: int,
    selected_positions: list[int],
    node_120_numbers: list[int],
    matrices: _EvaluationMatrices,
    ridge_alpha: float,
    summary_rows: list[dict[str, object]],
    selected_rows: list[dict[str, object]],
    segment_rows: list[dict[str, object]],
    per_node_rows: list[dict[str, object]],
) -> None:
    if any(row["run_id"] == run_id and row["method"] == method and row["k"] == k_value for row in summary_rows):
        return
    selected_node_numbers = [node_120_numbers[position] for position in selected_positions]
    metrics = evaluate_selected_positions(
        train_y=matrices.train_y,
        val_y=matrices.val_y,
        selected_positions=selected_positions,
        val_segment_masks=matrices.val_segment_masks,
        val_valid_rows=matrices.val_valid_rows,
        target_node_numbers=node_120_numbers,
        ridge_alpha=ridge_alpha,
    )
    summary_rows.append(
        {
            "run_id": run_id,
            "method": method,
            "k": k_value,
            **metrics["summary"],
            "selected_node_numbers": ";".join(str(node) for node in selected_node_numbers),
            "selected_node_1based": ";".join(str(node + 1) for node in selected_node_numbers),
        }
    )
    for row in selected_node_rows(selected_node_numbers, node_120_numbers):
        selected_rows.append({"run_id": run_id, "method": method, "k": k_value, **row})
    for row in metrics["segment_metrics"]:
        segment_rows.append({"run_id": run_id, "method": method, "k": k_value, **row})
    for row in metrics["per_node_metrics"]:
        per_node_rows.append({"run_id": run_id, "method": method, "k": k_value, **row})


def _write_forward_checkpoint(
    checkpoint_path: Path,
    run_id: str,
    selected_positions: list[int],
    node_120_numbers: list[int],
    score_history: list[dict[str, object]],
    max_k: int,
    worker_count: int,
    manifest: dict[str, object],
) -> None:
    checkpoint = {
        "run_id": run_id,
        "method": "forward_greedy",
        "completed_step": len(selected_positions),
        "max_k": max_k,
        "worker_count": worker_count,
        "selected_positions": selected_positions,
        "selected_node_numbers": [node_120_numbers[position] for position in selected_positions],
        "selected_node_1based": [node_120_numbers[position] + 1 for position in selected_positions],
        "score_history": score_history,
        "split": manifest.get("split"),
        "seed": manifest.get("seed"),
    }
    checkpoint_path.write_text(json.dumps(_json_safe(checkpoint), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _prepare_record(record: SuperfileRecord, node_120_numbers: list[int]) -> _PreparedRecord:
    target = extract_node_matrix(record, node_120_numbers)
    masks = build_segment_masks(record).as_dict()
    return _PreparedRecord(
        source_name=record.source_name,
        target=np.asarray(target, dtype=float),
        valid_rows=valid_rows_without_sentinel(target),
        segment_masks=masks,
    )


def _record_level_split(record_count: int, seed: int, val_fraction: float) -> tuple[list[int], list[int]]:
    if record_count < 1:
        raise ValueError("record_count must be positive")
    if record_count == 1:
        return [0], [0]
    indices = list(range(record_count))
    random.Random(seed).shuffle(indices)
    val_count = max(1, int(round(record_count * val_fraction)))
    val_count = min(val_count, record_count - 1)
    return sorted(indices[val_count:]), sorted(indices[:val_count])


def _evaluation_matrices(prepared: _PreparedData) -> _EvaluationMatrices:
    train_y = _stack_valid_targets(prepared.train_records)
    val_y = np.vstack([record.target for record in prepared.val_records])
    val_valid_rows = [include for record in prepared.val_records for include in record.valid_rows]
    val_segment_masks = {
        segment: [include for record in prepared.val_records for include in record.segment_masks[segment]]
        for segment in ("all", "p", "qrs", "stt")
    }
    return _EvaluationMatrices(
        train_y=train_y,
        val_y=val_y,
        val_valid_rows=val_valid_rows,
        val_segment_masks=val_segment_masks,
    )


def _stack_valid_targets(records: list[_PreparedRecord]) -> np.ndarray:
    rows = [record.target[np.asarray(record.valid_rows, dtype=bool)] for record in records]
    rows = [row for row in rows if row.size]
    if not rows:
        raise ValueError("no valid training rows remain after sentinel exclusion")
    return np.vstack(rows)


def _selection_order_for_method(
    method: str,
    train_y: np.ndarray,
    val_y: np.ndarray,
    val_segment_masks: dict[str, list[bool]],
    val_valid_rows: list[bool],
    max_k: int,
    seed: int,
    ridge_alpha: float,
    worker_count: int,
) -> list[int]:
    if method == "random":
        return random_order(train_y.shape[1], max_k, seed=seed)
    if method == "pca_qr":
        return pca_qr_order(train_y, max_k=max_k)
    if method == "forward_greedy":
        return forward_greedy_order(
            train_y=train_y,
            val_y=val_y,
            val_segment_masks=val_segment_masks,
            val_valid_rows=val_valid_rows,
            max_k=max_k,
            ridge_alpha=ridge_alpha,
            worker_count=worker_count,
        )
    raise ValueError(f"unsupported candidate selection method: {method}")


def _best_forward_candidate(
    selected: list[int],
    candidates: list[int],
    train_y: np.ndarray,
    val_y: np.ndarray,
    val_segment_masks: dict[str, list[bool]],
    val_valid_rows: list[bool],
    ridge_alpha: float,
) -> tuple[int, float]:
    results = [
        (
            candidate,
            _score_selected_positions(
                train_y=train_y,
                val_y=val_y,
                selected_positions=[*selected, candidate],
                val_segment_masks=val_segment_masks,
                val_valid_rows=val_valid_rows,
                ridge_alpha=ridge_alpha,
            ),
        )
        for candidate in candidates
    ]
    return _best_score_result(results)


def _score_selected_positions(
    train_y: np.ndarray,
    val_y: np.ndarray,
    selected_positions: list[int],
    val_segment_masks: dict[str, list[bool]],
    val_valid_rows: list[bool],
    ridge_alpha: float,
) -> float | None:
    metrics = evaluate_selected_positions(
        train_y=train_y,
        val_y=val_y,
        selected_positions=selected_positions,
        val_segment_masks=val_segment_masks,
        val_valid_rows=val_valid_rows,
        ridge_alpha=ridge_alpha,
    )
    score = metrics["summary"]["score"]
    return float(score) if score is not None else None


def _init_forward_worker(
    train_y: np.ndarray,
    val_y: np.ndarray,
    val_segment_masks: dict[str, list[bool]],
    val_valid_rows: list[bool],
    ridge_alpha: float,
) -> None:
    _FORWARD_WORKER_STATE.clear()
    _FORWARD_WORKER_STATE.update(
        {
            "train_y": train_y,
            "val_y": val_y,
            "val_segment_masks": val_segment_masks,
            "val_valid_rows": val_valid_rows,
            "ridge_alpha": ridge_alpha,
        }
    )


def _score_forward_candidate_worker(task: tuple[list[int], int]) -> tuple[int, float | None]:
    selected, candidate = task
    score = _score_selected_positions(
        train_y=_FORWARD_WORKER_STATE["train_y"],
        val_y=_FORWARD_WORKER_STATE["val_y"],
        selected_positions=[*selected, candidate],
        val_segment_masks=_FORWARD_WORKER_STATE["val_segment_masks"],
        val_valid_rows=_FORWARD_WORKER_STATE["val_valid_rows"],
        ridge_alpha=_FORWARD_WORKER_STATE["ridge_alpha"],
    )
    return candidate, score


def _best_score_result(results: list[tuple[int, float | None]]) -> tuple[int, float]:
    finite_results = [(candidate, float(score)) for candidate, score in results if score is not None]
    if not finite_results:
        raise ValueError("forward greedy could not find a finite-scoring candidate")
    return min(finite_results, key=lambda item: item[1])


def _set_single_thread_blas_defaults() -> None:
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ.setdefault(name, "1")


def _ridge_predict(train_x: np.ndarray, train_y: np.ndarray, val_x: np.ndarray, ridge_alpha: float) -> np.ndarray:
    x_mean = train_x.mean(axis=0, keepdims=True)
    y_mean = train_y.mean(axis=0, keepdims=True)
    train_x_centered = train_x - x_mean
    train_y_centered = train_y - y_mean
    lhs = train_x_centered.T @ train_x_centered
    lhs += ridge_alpha * np.eye(lhs.shape[0])
    rhs = train_x_centered.T @ train_y_centered
    try:
        coefficients = np.linalg.solve(lhs, rhs)
    except np.linalg.LinAlgError:
        coefficients = np.linalg.pinv(lhs) @ rhs
    return (val_x - x_mean) @ coefficients + y_mean


def _manifest(
    run_id: str,
    config_path: str | Path | None,
    raw_path: str | Path | None,
    node_label_path: str | Path | None,
    methods: list[str],
    k_values: list[int],
    seed: int,
    ridge_alpha: float,
    worker_count: int,
    resume: bool,
    max_runtime_minutes: float | None,
    progress_log_name: str,
    prepared: _PreparedData,
    matrices: _EvaluationMatrices,
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "config_path": str(config_path) if config_path is not None else None,
        "raw_path": str(raw_path) if raw_path is not None else None,
        "node_label_path": str(node_label_path) if node_label_path is not None else None,
        "methods": methods,
        "k_values": k_values,
        "seed": seed,
        "ridge_alpha": ridge_alpha,
        "worker_count": worker_count,
        "resume": resume,
        "max_runtime_minutes": max_runtime_minutes,
        "progress_log_name": progress_log_name,
        "checkpoint_file": FORWARD_GREEDY_CHECKPOINT,
        "task": "node_120_sparse_k_to_node_120",
        "status": "pending",
        "metric_status": "exploratory_candidate_selection_only",
        "primary_metric": "segment_balanced_nRMSE",
        "sentinel_policy": "exclude_rows_with_exact_9999_or_minus_9999_for_exploratory_scores",
        "target_node_count": len(prepared.node_120_numbers),
        "train_valid_sample_count": int(matrices.train_y.shape[0]),
        "val_sample_count": int(matrices.val_y.shape[0]),
        "val_valid_sample_count": int(sum(matrices.val_valid_rows)),
        "val_dropped_sentinel_sample_count": int(len(matrices.val_valid_rows) - sum(matrices.val_valid_rows)),
        "split": prepared.split_manifest,
        "git_commit": _git_commit(),
    }


def _write_outputs(
    paths,
    summary_rows: list[dict[str, object]],
    selected_rows: list[dict[str, object]],
    segment_rows: list[dict[str, object]],
    per_node_rows: list[dict[str, object]],
    manifest: dict[str, object],
) -> None:
    paths.root.mkdir(parents=True, exist_ok=True)
    paths.tracked_summary_md.parent.mkdir(parents=True, exist_ok=True)
    _write_csv(paths.summary_csv, summary_rows)
    _write_csv(paths.selected_nodes_csv, selected_rows)
    _write_csv(paths.segment_metrics_csv, segment_rows)
    _write_csv(paths.per_node_metrics_csv, per_node_rows)
    paths.run_manifest_json.write_text(json.dumps(_json_safe(manifest), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = _report_markdown(summary_rows, manifest)
    paths.report_md.write_text(report, encoding="utf-8")
    paths.tracked_summary_md.write_text(report, encoding="utf-8")


def _report_markdown(summary_rows: list[dict[str, object]], manifest: dict[str, object]) -> str:
    sorted_rows = sorted(summary_rows, key=lambda row: float(row["score"]) if row["score"] is not None else float("inf"))
    lines = [
        "# BSPM Candidate Selection Report",
        "",
        f"- Run id: `{manifest['run_id']}`",
        f"- Task: `{manifest['task']}`",
        f"- Metric status: `{manifest['metric_status']}`",
        f"- Primary metric: `{manifest['primary_metric']}`",
        f"- Sentinel policy: `{manifest['sentinel_policy']}`",
        f"- Train records: `{manifest['split']['train_record_count']}`",
        f"- Validation records: `{manifest['split']['val_record_count']}`",
        "",
        "## Top Results",
        "",
        "| method | k | score | qrs nRMSE | stt nRMSE | spatial RMS uV | spatial corr | selected nodes |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in sorted_rows[:12]:
        lines.append(
            "| {method} | {k} | {score} | {qrs} | {stt} | {rms} | {corr} | `{nodes}` |".format(
                method=row["method"],
                k=row["k"],
                score=_format_float(row["score"]),
                qrs=_format_float(row["qrs_nRMSE"]),
                stt=_format_float(row["stt_nRMSE"]),
                rms=_format_float(row["spatial_rms_error_uV"]),
                corr=_format_float(row["frame_spatial_corr"]),
                nodes=row["selected_node_1based"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Lower `segment_balanced_nRMSE` is better. These results are exploratory and must not be treated as final test metrics.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _json_safe(value):
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def _format_float(value: object) -> str:
    if value is None:
        return ""
    return f"{float(value):.6g}"


def _format_duration(seconds: float) -> str:
    total = int(round(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _validate_k(k_value: int, node_count: int) -> None:
    if k_value < 1 or k_value > node_count:
        raise ValueError(f"k must be in 1..{node_count}, found {k_value}")


def _git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()
