# PRD

## Goal
Build a reusable ML research harness for training, evaluating, diagnosing, and iterating on models from data.

## Supported Tasks
- classification
- regression
- segmentation
- reconstruction
- localization
- forecasting
- representation learning
- fine-tuning

## Inputs And Outputs
- Input data type: project-specific, declared in `DATA_SPEC.md`.
- Output type: project-specific, declared in the active experiment config.
- Target task: one supported task per project baseline.

## Metrics
- Primary metric: define exactly one per project before comparing experiments.
- Secondary metrics: add metrics that explain behavior.
- Safety metrics: add metrics that must not degrade while optimizing the primary metric.

## Thresholds
- Success threshold: project-specific and fixed before full training.
- Failure threshold: project-specific and fixed before full training.

## Non-Negotiable Constraints
- Do not modify the final test split without approval.
- Do not modify the primary metric without approval.
- Do not modify label generation rules without approval.
- Do not run full training without approval.

## Human Approval Required
- metric definition changes
- dataset split changes
- label generation changes
- new external dependencies
- full training jobs
- Slurm submissions
- multi-GPU jobs

