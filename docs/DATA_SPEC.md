# DATA_SPEC

## Purpose
This template file defines the data contract that each instantiated project must
fill in before real model comparison.

## Locations
- Raw data location: project-specific.
- Processed data location: project-specific experiment output under
  `experiments/`.
- Metadata, manifests, and split files: project-specific and versioned.

## Schema
- Record identifier: define the stable entity or sample identifier.
- Input fields: define names, shapes, dtypes, and units.
- Target fields: define names, shapes, dtypes, units, and generation rules.
- Grouping key: define the entity level that must stay within a single split.

## Labels And Targets
- Label or target generation rules require human approval before changes.
- Deterministic target derivations must be documented here before comparison.
- Any weak labels, pseudo-labels, masks, or exclusions must include provenance.

## Splits
- Split format: project-specific.
- Final test split must not change without explicit approval.
- Leakage is forbidden: samples from the same protected grouping key must not be
  split across train/validation/test.
- If stronger grouping metadata becomes available, splits must be upgraded
  before final evaluation.

## Dataset Versioning
Every experiment must record dataset name, dataset version, source identity,
split version, preprocessing version, and relevant metadata versions.

## Allowed Preprocessing
- Deterministic preprocessing declared in config or data docs.
- Training-only augmentation that does not leak validation or test information.
- Unit conversion or normalization only when declared before evaluation.

## Forbidden Preprocessing
- Any preprocessing that uses validation or test labels during training.
- Any split-dependent filtering not documented before evaluation.
- Any selection procedure fit on validation or test records unless explicitly
  approved as evaluation-only analysis.

## Required Audits
- missing values
- invalid structure or unexpected shapes
- duplicate samples
- split leakage
- entity-level leakage if applicable
- class, target, or domain imbalance
- train/validation/test distribution mismatch
- feature and target value ranges
- sentinel, placeholder, or out-of-domain values

Worked examples may define a concrete data contract under `examples/`.
