#!/usr/bin/env python3
"""BSPM project-specific command entrypoint."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from examples.bspm.bspm_harness.evaluators.bspm_candidate_selection import (  # noqa: E402
    SUPPORTED_METHODS,
    run_candidate_selection_from_paths,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="BSPM sparse reconstruction utilities.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    select = subparsers.add_parser("select-candidates", help="Run exploratory sparse-node selection baselines.")
    select.add_argument(
        "--config",
        default="examples/bspm/configs/bspm_baseline.yaml",
        help="Path to BSPM example config.",
    )
    select.add_argument("--raw-path", help="Override Superfile raw path.")
    select.add_argument("--node-label-path", help="Override node_label.xlsx path.")
    select.add_argument("--run-id", help="Run id for output directories.")
    select.add_argument("--output-dir", help="Raw output root directory.")
    select.add_argument("--report-dir", help="Tracked summary directory.")
    select.add_argument("--max-records", type=int, help="Limit records for smoke runs.")
    select.add_argument("--seed", type=int, help="Override random seed.")
    select.add_argument("--val-fraction", type=float, default=0.2, help="Exploratory validation fraction.")
    select.add_argument("--ridge-alpha", type=float, default=1.0, help="Ridge alpha for reconstruction scoring.")
    select.add_argument("--workers", type=int, help="CPU worker processes for forward_greedy scoring.")
    select.add_argument("--resume", action="store_true", help="Resume forward_greedy from checkpoint if present.")
    select.add_argument("--max-runtime-minutes", type=float, help="Cleanly stop after this many minutes.")
    select.add_argument(
        "--progress-log-name",
        default="forward_greedy_progress.csv",
        help="Progress CSV filename inside the run output directory.",
    )
    select.add_argument("--k", nargs="+", type=int, help="Candidate k values.")
    select.add_argument("--methods", nargs="+", choices=SUPPORTED_METHODS, help="Candidate selection methods.")

    args = parser.parse_args()
    if args.command == "select-candidates":
        return _select_candidates(args)
    parser.error(f"unknown command: {args.command}")
    return 2


def _select_candidates(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    if not config_path.exists():
        raise FileNotFoundError(f"config not found: {config_path}")
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    raw_path = args.raw_path or cfg["data"]["raw_path"]
    node_label_path = args.node_label_path or cfg["data"]["node_label_path"]
    candidate_cfg = cfg.get("candidate_selection", {})
    run_id = args.run_id or _default_run_id()
    output_dir = args.output_dir or candidate_cfg.get("output_dir", "examples/bspm/experiments/candidate_selection_v1")
    report_dir = args.report_dir or candidate_cfg.get("report_dir", "examples/bspm/reports/candidate_selection_v1")
    seed = args.seed if args.seed is not None else int(cfg.get("run", {}).get("seed", 42))
    k_values = args.k or candidate_cfg.get("k_values") or cfg["data"].get("sparse_node_counts") or [3, 6]
    methods = args.methods or candidate_cfg.get("methods") or ["random", "pca_qr", "forward_greedy"]
    workers = args.workers if args.workers is not None else int(candidate_cfg.get("worker_count", 1))

    result = run_candidate_selection_from_paths(
        raw_path=raw_path,
        node_label_path=node_label_path,
        run_id=run_id,
        k_values=[int(value) for value in k_values],
        methods=list(methods),
        output_dir=output_dir,
        report_dir=report_dir,
        max_records=args.max_records,
        seed=seed,
        val_fraction=args.val_fraction,
        ridge_alpha=args.ridge_alpha,
        worker_count=workers,
        resume=args.resume,
        max_runtime_minutes=args.max_runtime_minutes,
        progress_log_name=args.progress_log_name,
        config_path=config_path,
    )
    print(f"candidate_selection_run_id: {result.run_id}")
    print(f"raw_output_dir: {result.output_root}")
    print(f"tracked_summary: {result.tracked_summary}")
    print(f"summary_rows: {len(result.summary_rows)}")
    return 0


def _default_run_id() -> str:
    return "candidate_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


if __name__ == "__main__":
    raise SystemExit(main())
