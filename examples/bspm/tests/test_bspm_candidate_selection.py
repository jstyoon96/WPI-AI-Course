from pathlib import Path
import json

from examples.bspm.bspm_harness.data.bspm_superfile import NODE_COUNT, SuperfileHeader, SuperfileRecord
from examples.bspm.bspm_harness.evaluators.bspm_candidate_selection import (
    forward_greedy_order,
    pca_qr_order,
    random_order,
    run_candidate_selection,
)


def test_pca_qr_and_random_return_node_positions_inside_universe():
    records = [_synthetic_record(record_index) for record_index in range(3)]
    node_120_numbers = list(range(120))
    result = run_candidate_selection(
        records=records,
        node_120_numbers=node_120_numbers,
        run_id="unit_candidates",
        k_values=[3],
        methods=["random", "pca_qr"],
        output_dir="/tmp/bspm_candidate_unit_experiments",
        report_dir="/tmp/bspm_candidate_unit_reports",
    )

    assert len(result.summary_rows) == 2
    for row in result.selected_node_rows:
        assert 0 <= row["node_120_position"] < 120
        assert row["node_number"] in node_120_numbers


def test_forward_greedy_order_is_deterministic_for_same_inputs():
    records = [_synthetic_record(record_index) for record_index in range(3)]
    result = run_candidate_selection(
        records=records,
        node_120_numbers=list(range(120)),
        run_id="unit_forward",
        k_values=[2],
        methods=["forward_greedy"],
        output_dir="/tmp/bspm_candidate_unit_experiments",
        report_dir="/tmp/bspm_candidate_unit_reports",
    )

    selected = [row for row in result.selected_node_rows if row["method"] == "forward_greedy"]
    assert [row["selection_order"] for row in selected] == [1, 2]
    assert len({row["node_number"] for row in selected}) == 2
    assert result.summary_rows[0]["score"] is not None


def test_forward_greedy_supports_cpu_workers():
    records = [_synthetic_record(record_index) for record_index in range(3)]
    result = run_candidate_selection(
        records=records,
        node_120_numbers=list(range(120)),
        run_id="unit_forward_workers",
        k_values=[2],
        methods=["forward_greedy"],
        output_dir="/tmp/bspm_candidate_unit_experiments",
        report_dir="/tmp/bspm_candidate_unit_reports",
        worker_count=2,
    )

    assert result.manifest["worker_count"] == 2
    assert len(result.selected_node_rows) == 2


def test_forward_greedy_checkpoint_and_resume_matches_uninterrupted_run(tmp_path: Path):
    records = [_synthetic_record(record_index) for record_index in range(3)]
    node_120_numbers = list(range(120))
    interrupted_output = tmp_path / "interrupted"
    report_dir = tmp_path / "reports"

    interrupted = run_candidate_selection(
        records=records,
        node_120_numbers=node_120_numbers,
        run_id="resume_case",
        k_values=[1, 2],
        methods=["forward_greedy"],
        output_dir=interrupted_output,
        report_dir=report_dir,
        max_runtime_minutes=0,
        resume=True,
    )

    checkpoint_path = interrupted.output_root / "forward_greedy_checkpoint.json"
    progress_path = interrupted.output_root / "forward_greedy_progress.csv"
    assert checkpoint_path.is_file()
    assert progress_path.is_file()
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    assert checkpoint["completed_step"] == 1
    assert interrupted.manifest["status"] == "stopped_early"

    resumed = run_candidate_selection(
        records=records,
        node_120_numbers=node_120_numbers,
        run_id="resume_case",
        k_values=[1, 2],
        methods=["forward_greedy"],
        output_dir=interrupted_output,
        report_dir=report_dir,
        resume=True,
    )
    uninterrupted = run_candidate_selection(
        records=records,
        node_120_numbers=node_120_numbers,
        run_id="uninterrupted_case",
        k_values=[2],
        methods=["forward_greedy"],
        output_dir=tmp_path / "uninterrupted",
        report_dir=report_dir,
    )

    resumed_k2 = [row for row in resumed.selected_node_rows if row["k"] == 2]
    uninterrupted_k2 = [row for row in uninterrupted.selected_node_rows if row["k"] == 2]
    assert [row["node_number"] for row in resumed_k2] == [row["node_number"] for row in uninterrupted_k2]
    assert resumed.manifest["status"] == "complete"


def test_candidate_selection_writes_storage_contract(tmp_path: Path):
    records = [_synthetic_record(record_index) for record_index in range(3)]
    output_dir = tmp_path / "experiments"
    report_dir = tmp_path / "reports"

    result = run_candidate_selection(
        records=records,
        node_120_numbers=list(range(120)),
        run_id="contract_smoke",
        k_values=[2],
        methods=["random"],
        output_dir=output_dir,
        report_dir=report_dir,
    )

    assert (result.output_root / "summary.csv").is_file()
    assert (result.output_root / "selected_nodes.csv").is_file()
    assert (result.output_root / "per_node_metrics.csv").is_file()
    assert (result.output_root / "segment_metrics.csv").is_file()
    assert (result.output_root / "run_manifest.json").is_file()
    assert (result.output_root / "report.md").is_file()
    assert result.tracked_summary.is_file()


def test_low_level_orders_have_requested_length():
    records = [_synthetic_record(record_index) for record_index in range(3)]
    result = run_candidate_selection(
        records=records,
        node_120_numbers=list(range(120)),
        run_id="order_fixture",
        k_values=[2],
        methods=["random"],
        output_dir="/tmp/bspm_candidate_unit_experiments",
        report_dir="/tmp/bspm_candidate_unit_reports",
    )
    train_y = result.manifest["train_valid_sample_count"]

    assert train_y > 0
    assert len(random_order(120, 3, seed=42)) == 3


def _synthetic_record(record_index: int) -> SuperfileRecord:
    sample_numbers = list(range(1, 7))
    flags = [
        [1, 1, 0, 0, 0],
        [1, 1, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 1, 1],
        [0, 0, 0, 1, 1],
    ]
    node_potentials = []
    for sample_number in sample_numbers:
        row = []
        for node_number in range(NODE_COUNT):
            row.append(float((sample_number + record_index) * (1.0 + node_number / 1000.0)))
        node_potentials.append(row)

    return SuperfileRecord(
        source_name=f"node{record_index + 1:04d}.txt",
        header=SuperfileHeader(
            serial=record_index + 1,
            record_id=f"synthetic{record_index}",
            sampling_interval_ms=2.0,
            p_onset_ms=0.0,
            p_offset_ms=2.0,
            qrs_onset_ms=4.0,
            qrs_offset_ms=6.0,
            t_offset_ms=10.0,
        ),
        sample_numbers=sample_numbers,
        flags=flags,
        limb_potentials=[[0.0, 0.0, 0.0] for _ in sample_numbers],
        node_potentials=node_potentials,
    )
