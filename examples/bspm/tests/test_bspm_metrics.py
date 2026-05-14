import pytest

from examples.bspm.bspm_harness.data.bspm_superfile import NODE_COUNT, parse_superfile_text
from examples.bspm.bspm_harness.evaluators.bspm_metrics import (
    build_segment_masks,
    compute_candidate_metrics,
    selected_node_rows,
    valid_rows_without_sentinel,
)
from harness.reports.contracts import candidate_selection_paths


def test_candidate_metrics_report_zero_error_by_segment():
    record = _record_with_segments()
    target = [
        [1.0, 2.0],
        [2.0, 4.0],
        [10.0, 20.0],
        [20.0, 40.0],
        [5.0, 10.0],
        [4.0, 8.0],
    ]

    metrics = compute_candidate_metrics(
        target=target,
        prediction=[row[:] for row in target],
        segment_masks=build_segment_masks(record),
        target_node_numbers=[15, 16],
    )

    summary = metrics["summary"]
    assert summary["segment_balanced_nRMSE"] == pytest.approx(0.0)
    assert summary["all_nRMSE"] == pytest.approx(0.0)
    assert summary["p_nRMSE"] == pytest.approx(0.0)
    assert summary["qrs_nRMSE"] == pytest.approx(0.0)
    assert summary["stt_nRMSE"] == pytest.approx(0.0)
    assert summary["spatial_rms_error_uV"] == pytest.approx(0.0)
    assert summary["frame_spatial_corr"] == pytest.approx(1.0)
    assert metrics["segment_metrics"][1]["segment"] == "p"
    assert metrics["segment_metrics"][1]["sample_count"] == 2
    assert metrics["per_node_metrics"][0]["target_node_number"] == 15
    assert metrics["per_node_metrics"][0]["correlation"] == pytest.approx(1.0)


def test_candidate_metrics_skip_invalid_p_segment_and_sentinel_rows():
    record = _record_with_segments(p_onset=-1.0, p_offset=-1.0)
    target = [[1.0, 2.0], [9999.0, 4.0], [10.0, 20.0], [20.0, 40.0], [5.0, 10.0], [4.0, 8.0]]
    prediction = [[row[0], row[1]] for row in target]
    valid_rows = valid_rows_without_sentinel(target, prediction)

    metrics = compute_candidate_metrics(
        target=target,
        prediction=prediction,
        segment_masks=build_segment_masks(record),
        valid_row_mask=valid_rows,
    )

    summary = metrics["summary"]
    assert summary["p_nRMSE"] is None
    assert summary["segment_balanced_nRMSE"] == pytest.approx(0.0)
    assert summary["valid_sample_count"] == 5
    assert summary["dropped_sentinel_sample_count"] == 1


def test_selected_node_rows_include_absolute_and_node_120_positions():
    rows = selected_node_rows(selected_node_numbers=[15, 42, 83], node_120_numbers=[15, 16, 42, 83])

    assert rows == [
        {"selection_order": 1, "node_number": 15, "node_1based": 16, "node_120_position": 0},
        {"selection_order": 2, "node_number": 42, "node_1based": 43, "node_120_position": 2},
        {"selection_order": 3, "node_number": 83, "node_1based": 84, "node_120_position": 3},
    ]


def test_candidate_selection_paths_define_raw_outputs_and_tracked_summary():
    paths = candidate_selection_paths("smoke_run")

    assert str(paths.root) == "experiments/candidate_selection_v1/smoke_run"
    assert paths.summary_csv.name == "summary.csv"
    assert paths.selected_nodes_csv.name == "selected_nodes.csv"
    assert paths.per_node_metrics_csv.name == "per_node_metrics.csv"
    assert paths.segment_metrics_csv.name == "segment_metrics.csv"
    assert paths.run_manifest_json.name == "run_manifest.json"
    assert paths.report_md.name == "report.md"
    assert str(paths.tracked_summary_md) == "reports/candidate_selection_v1/smoke_run_summary.md"


def _record_with_segments(p_onset: float = 0.0, p_offset: float = 2.0):
    rows = []
    flag_rows = [
        [1, 1, 0, 0, 0],
        [1, 1, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 1, 1],
        [0, 0, 0, 1, 1],
    ]
    for sample_number, flags in enumerate(flag_rows, start=1):
        limb = [0, 0, 0]
        nodes = list(range(sample_number, sample_number + NODE_COUNT))
        rows.append(" ".join(str(value) for value in [1, sample_number, *flags, *limb, *nodes]))
    return parse_superfile_text(
        "\n".join(
            [
                f"1 record001 2.0 {p_onset} {p_offset} 4.0 6.0 10.0",
                *rows,
            ]
        ),
        "node0001.txt",
    )
