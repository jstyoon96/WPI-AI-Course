# METRIC_SPEC

## Primary Metric
Define exactly one primary metric per project before model comparison.

## Secondary Metrics
Define explanatory metrics such as loss, calibration, per-class score, or subgroup score.

## Safety Metrics
Define metrics that must not degrade while optimizing the primary metric.

## Diagnostic Metrics
Add metrics that help classify failures, such as train/validation gap, NaN counts, worst subgroup score, or convergence indicators.

## Aggregation
Aggregation method must be declared before final evaluation.

## Subgroup Reporting
Report subgroup metrics when meaningful grouping metadata exists.

## Variance
Add confidence intervals, bootstrap estimates, or repeated-seed variance when the project requires statistical comparison.

## Approval Policy
Codex must not modify metric definitions unless the task explicitly asks for a metric change.

