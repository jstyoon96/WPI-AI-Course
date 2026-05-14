# EDD

## Current Result
No experiments have run yet. This repository currently contains the initial harness skeleton.

## Failure Diagnosis
Not applicable until an experiment produces metrics, audit reports, or training logs.

## Hypothesis
The first implementation goal is reproducibility and safety rather than model improvement.

## Proposed Change
Create a minimal general-purpose harness skeleton with policy docs, configs, CLI placeholders, package directories, and smoke tests.

## Fixed Variables
- dataset split
- primary metric
- evaluation code
- baseline preprocessing

## Cheap Validation
Run unit tests, smoke imports, dry train placeholder, fast-dev-run placeholder, small eval placeholder, and report placeholder.

## Promotion Rule
Promote beyond skeleton only when config validation, imports, and placeholder command checks pass.

## Risks
- The harness currently has interfaces and placeholders, not real training logic.
- Project-specific data contracts and metrics still need to be defined before real experiments.

## Rollback
Remove the initial skeleton files or revert the corresponding commit once the repository is initialized.

