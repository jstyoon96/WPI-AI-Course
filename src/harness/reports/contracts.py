"""Experiment output contract helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExperimentPaths:
    root: Path
    config: Path
    resolved_config: Path
    git_commit: Path
    dataset_manifest: Path
    train_log: Path
    metrics_summary: Path
    metrics_by_group: Path
    failure_report: Path
    audit_report: Path
    next_experiment_proposal: Path
    artifacts: Path


@dataclass(frozen=True)
class CandidateSelectionPaths:
    root: Path
    summary_csv: Path
    selected_nodes_csv: Path
    per_node_metrics_csv: Path
    segment_metrics_csv: Path
    run_manifest_json: Path
    report_md: Path
    tracked_summary_md: Path


def experiment_paths(run_id: str, output_dir: str | Path = "experiments") -> ExperimentPaths:
    root = Path(output_dir) / run_id
    return ExperimentPaths(
        root=root,
        config=root / "config.yaml",
        resolved_config=root / "resolved_config.yaml",
        git_commit=root / "git_commit.txt",
        dataset_manifest=root / "dataset_manifest.json",
        train_log=root / "train.log",
        metrics_summary=root / "metrics_summary.json",
        metrics_by_group=root / "metrics_by_group.csv",
        failure_report=root / "failure_report.json",
        audit_report=root / "audit_report.json",
        next_experiment_proposal=root / "next_experiment_proposal.md",
        artifacts=root / "artifacts",
    )


def candidate_selection_paths(
    run_id: str,
    output_dir: str | Path = "experiments/candidate_selection_v1",
    report_dir: str | Path = "reports/candidate_selection_v1",
) -> CandidateSelectionPaths:
    root = Path(output_dir) / run_id
    return CandidateSelectionPaths(
        root=root,
        summary_csv=root / "summary.csv",
        selected_nodes_csv=root / "selected_nodes.csv",
        per_node_metrics_csv=root / "per_node_metrics.csv",
        segment_metrics_csv=root / "segment_metrics.csv",
        run_manifest_json=root / "run_manifest.json",
        report_md=root / "report.md",
        tracked_summary_md=Path(report_dir) / f"{run_id}_summary.md",
    )
