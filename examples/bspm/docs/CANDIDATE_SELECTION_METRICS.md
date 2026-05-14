# Candidate Selection Metrics

These metrics are exploratory ranking metrics for BSPM v1 candidate-node
selection. They are not final approved test metrics.

## Ranking Metric

Primary candidate ranking uses `segment_balanced_nRMSE` over `node_120 ->
node_120` reconstruction:

```text
0.45 * qrs_nRMSE
+ 0.25 * stt_nRMSE
+ 0.15 * p_nRMSE
+ 0.15 * all_nRMSE
```

If a segment is unavailable, for example P fiducials are invalid with
`p_onset = -1`, the score is re-normalized over the available finite segments
and the skipped segment count must be reported.

The initial nRMSE definition is:

```text
nRMSE = RMSE_uV / target_RMS_uV
```

## Secondary Metrics

- `spatial_rms_error_uV`: mean frame-wise RMS voltage error across target nodes.
- `frame_spatial_corr`: mean Pearson correlation between measured and
  reconstructed 120-node map frames.
- `per_node_nRMSE`: target-node-specific reconstruction error.

## Beat Segments

Segment masks are derived from Superfile header fiducials and row flags:

- `p`: P-wave segment, skipped when P fiducials are invalid.
- `qrs`: QRS segment.
- `stt`: post-QRS through T-offset segment.
- `all`: all valid samples.

Exact `9999` and `-9999` node values are excluded from exploratory candidate
scores, and excluded row counts must be stored with the metrics. This is not a
final imputation or preprocessing policy.

## Storage Contract

Raw candidate outputs go under:

```text
examples/bspm/experiments/candidate_selection_v1/<run_id>/
```

Expected raw outputs:

- `summary.csv`
- `selected_nodes.csv`
- `per_node_metrics.csv`
- `segment_metrics.csv`
- `run_manifest.json`
- `report.md`

Curated human-readable summaries go under:

```text
examples/bspm/reports/candidate_selection_v1/<run_id>_summary.md
```

## Initial Selection Methods

- `random`: deterministic sanity baseline.
- `pca_qr`: center the training `node_120` matrix, compute SVD/PCA modes, then
  use QR pivoting to convert modes into actual node positions.
- `forward_greedy`: add one node at a time using validation
  `segment_balanced_nRMSE`. Candidate scoring supports CPU worker processes for
  Turing-style runs; keep BLAS thread counts at 1 when using multiple workers.
