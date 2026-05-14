# BSPM Research Plan

## Project Question

What is the minimum subset of torso-surface nodes required to reconstruct a
larger BSPM node set with acceptable spatial and temporal fidelity?

The first implementation target is sparse-k reconstruction within the
120-node-labeled subset: `k selected nodes from node_120 -> all node_120`.
After that pipeline is validated, the same structure will extend to full-field
targets such as `k -> 352`.

## Data Interpretation

The Dalhousie/Superfile records are high-density body surface potential mapping
records, not ordinary 12-lead ECG files. Each sample row contains:

- serial number and sample number
- five segment flags
- RA, LA, and LL limb electrode potentials
- 352 torso-surface scalar potentials

The 352-node signal is a time-varying scalar potential field sampled on the
torso surface. Node coordinates, if available, provide geometry, but each node
value is a scalar potential rather than a 3D vector.

The `node_label.xlsx` workbook defines node sets used by this project:

- `node_120`: the 120-node set used as the v1 sparse-selection universe and
  reconstruction target.
- `node_352`: all 352 torso nodes, retained for later full BSPM reconstruction.
- `precordial_leads` and `easi_leads`: metadata retained for later analysis,
  not used by the v1 data pipeline.

## Derived 12-Lead Definitions

Limb leads:

```text
Lead I   = LA - RA
Lead II  = LL - RA
Lead III = LL - LA
aVR      = -(Lead I + Lead II) / 2
aVL      =  (Lead I - Lead III) / 2
aVF      =  (Lead II + Lead III) / 2
```

Precordial leads use one-based Superfile node labels:

```text
V1 = node169
V2 = node171
V3 = (node192 + node193) / 2
V4 = node216
V5 = (node217 + 2 * node218) / 3
V6 = node219
```

## Experiment Phases

1. Dataset audit: parse all Superfile records, confirm sampling intervals,
   sample lengths, fiducial timing ranges, amplitude ranges, missing values,
   and node-count consistency.
2. Node-label audit: parse `node_label.xlsx`, verify 352 zero-based node rows,
   exactly 120 `node_120` flags, and exactly 352 `node_352` flags.
3. Sparse-k data contract: build list-backed smoke batches where inputs are
   `[T, k]` selected from `node_120` and v1 targets are `[T, 120]`.
4. Low-rank feasibility: run PCA/SVD on the 120-node target set first, then
   compare with 352-node full-field targets later.
5. Minimal-node baselines: compare random subsets, PCA/QR selected subsets, and
   greedy forward selected subsets over k = 3, 6, 8, 12, 16, 24, 32, 48, 64.
6. Reconstruction modeling: start with ridge regression and reduced-rank
   regression before temporal CNN or graph-based models.
7. Derived 12-lead evaluation: defer until the sparse-k BSPM reconstruction
   pipeline is validated.

Candidate selection metrics and output storage are defined in
`docs/CANDIDATE_SELECTION_METRICS.md`. The v1 ranking score is exploratory
`segment_balanced_nRMSE`, with spatial RMS error and frame-wise spatial
correlation stored as secondary BSPM map-fidelity metrics.

## Initial Success Criteria To Review

These are planning targets, not locked metric definitions:

- high frame-wise spatial correlation across the 120-node v1 target set
- low normalized RMSE for sparse-k reconstruction targets
- high lead-wise correlation for derived 12-lead ECG in later phases
- preserved QRS/ST/T morphology and extrema locations

Metric definitions and final thresholds still require explicit approval before
model comparison or final test evaluation.
