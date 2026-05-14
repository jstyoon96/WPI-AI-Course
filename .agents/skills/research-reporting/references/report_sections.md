# Report Section Playbook

Use this playbook for formal Markdown or HTML reports. Each section must pass
the same contract: purpose, required inputs, output shape, quality gate, and
failure action.

## Shared Quality Contract

- Purpose: answer one clear reader question.
- Required inputs: cite run ids, configs, metrics, figures, tables, commits, or
  explicit assumptions.
- Output shape: use short paragraphs, compact tables, and labeled figures.
- Quality gate: claims must match evidence, metric direction must be explicit,
  and caveats must not be hidden.
- Failure action: if evidence is missing, write the section as a limitation or
  open question instead of inventing a result.

## Title And Metadata

- Purpose: identify what the artifact covers and how to reproduce its context.
- Required inputs: topic, date, author/context, repository commit when
  available, run ids, and artifact status.
- Output shape: title block plus a short artifact status note.
- Quality gate: readers can trace the report to the underlying run context.

## Executive Summary

- Purpose: state the decision, recommendation, or most important finding.
- Required inputs: primary metric, selected comparison, caveats, and next step.
- Output shape: 3-5 bullets or one short paragraph plus decision marker.
- Quality gate: no claim is stronger than the evidence later in the report.

## Task, Data, And Split

- Purpose: explain what was predicted, reconstructed, classified, ranked, or
  measured.
- Required inputs: task formulation, data source, split policy, target
  definition, and label status.
- Output shape: short prose plus a compact table when multiple datasets,
  cohorts, windows, or splits are involved.
- Quality gate: split and label rules are explicit and unchanged unless the
  user approved a change.

## Method And Protocol

- Purpose: make the comparison reproducible enough to review.
- Required inputs: model/baseline family, config path, preprocessing,
  evaluation protocol, training mode, and important fixed variables.
- Output shape: concise method description with config/run references.
- Quality gate: implementation detail is sufficient for reproduction but does
  not bury the main result.

## Metrics

- Purpose: define how success is measured.
- Required inputs: primary metric, secondary metrics, directionality, unit,
  aggregation, and final-vs-proxy status.
- Output shape: metric table with `metric`, `direction`, `scope`, and `status`.
- Quality gate: metric definitions are not silently changed and every result
  table/figure uses the same names.

## Results

- Purpose: present evidence for the report's main claims.
- Required inputs: tables, figures, run ids, confidence/error bars when
  available, and comparison baseline.
- Output shape: one main result table or figure per claim, followed by a short
  interpretation.
- Quality gate: axes, units, metric direction, selected points, and comparison
  groups are readable and labeled.

## Interpretation And Decision

- Purpose: explain what the evidence means for the next action.
- Required inputs: result deltas, failure taxonomy signal if available, known
  constraints, and approval gates.
- Output shape: decision table or short recommendation paragraph.
- Quality gate: recommendations distinguish evidence, inference, and
  speculation.

## Limitations, Risks, And Caveats

- Purpose: prevent overclaiming and make review risks visible.
- Required inputs: non-final status, missing runs, small samples, proxy metrics,
  data limitations, or tool/rendering limitations.
- Output shape: bullet list with concrete risk and likely impact.
- Quality gate: every major caveat from the evidence appears before the final
  recommendation.

## Next Experiment

- Purpose: propose the smallest useful follow-up.
- Required inputs: current failure mode, cheapest validation, fixed variables,
  approval requirements, and expected evidence.
- Output shape: one recommended next step plus optional alternatives.
- Quality gate: no full training, Slurm submission, split change, metric change,
  or label-rule change is proposed as already-approved unless explicitly
  approved by the user.
