# Deck Section Playbook

Use this playbook for lab meeting decks, project-review decks, and report-to-
deck conversion. A deck is not a compressed report. It is a live narrative with
one takeaway per slide and enough evidence for the audience to trust the story.

## Shared Slide Contract

- Purpose: every slide answers one audience question.
- Required inputs: takeaway, evidence object, source/run context, caveat status,
  and speaker intent.
- Output shape: assertion title, one dominant visual/table/diagram, and minimal
  supporting text.
- Quality gate: a viewer can understand the slide's main point from the title
  and visual within a few seconds.
- Failure action: split the slide, move detail to appendix/report, or rewrite
  the claim if the slide carries multiple messages.

## Three-Part WPI Deck Format

Use this format for WPI-light research decks. Treat it as a layout family, not
as fixed coordinates.

### First Page

- Purpose: introduce the project and presenter context.
- Required inputs: project title, presenter/author, date or meeting context,
  and one-sentence takeaway when available.
- Output shape: large centered title, small presenter/context line, bottom
  crimson band, small crimson accent, and generous whitespace.
- Quality gate: no dense tables, figures, method detail, or multi-bullet
  summaries on the first page.

### Body

- Purpose: carry the main evidence story.
- Required inputs: assertion title, one evidence object, source/run context,
  caveat status, and slide number.
- Output shape: top-left assertion title, left crimson vertical accent, broad
  content field, compact notes or labels, restrained gray/off-white structure,
  and small bottom-right slide number.
- Quality gate: every body slide uses the same visual skeleton while varying
  only the evidence object, labels, and section-specific content.

### Conclusion

- Purpose: close with the recommendation, phase plan, or next experiment.
- Required inputs: final claim, decision or phase list, limitations, approval
  constraints, and next recommended step.
- Output shape: same skeleton as a body slide, with the main area focused on a
  recommendation card, decision table, or phase plan.
- Quality gate: the conclusion does not introduce stronger claims than the body
  evidence supports and leaves the audience with one concrete next action.

## Title And Takeaway

- Purpose: frame the project and the one-sentence conclusion.
- Required inputs: topic, audience, presenter/context, date, and artifact
  status.
- Output shape: use the `First Page` layout: title, short takeaway, optional
  run/context line, bottom crimson band, and small crimson accent.
- Quality gate: the first slide makes the deck's purpose obvious without a
  generic subtitle.

## Objective And Task

- Purpose: define the problem and why it matters.
- Required inputs: task formulation, target, audience-relevant motivation, and
  success criterion.
- Output shape: one claim plus a compact task diagram or comparison frame.
- Quality gate: avoids jargon unless the audience is known to share it.

## Data And Split

- Purpose: show what evidence the model/report is allowed to use.
- Required inputs: data source, split policy, target/label status, and final-vs-
  proxy evaluation status.
- Output shape: split diagram, cohort/table summary, or concise data card.
- Quality gate: no ambiguity about what is train/validation/test/proxy.

## Method Overview

- Purpose: give just enough mechanism to interpret results.
- Required inputs: baseline/model family, preprocessing, config, and fixed
  variables.
- Output shape: simple pipeline diagram or model comparison panel.
- Quality gate: methods do not crowd out the result story.

## Protocol And Metrics

- Purpose: make evaluation rules legible before showing outcomes.
- Required inputs: primary metric, secondary metrics, directionality, units,
  aggregation, and promotion status.
- Output shape: metric card or small table.
- Quality gate: each metric includes `higher is better` or `lower is better`.

## Key Figure Or Curve

- Purpose: present the strongest evidence object.
- Required inputs: figure/table asset, run ids, selected point or comparison,
  and caveat.
- Output shape: one large visual with direct labels and a short evidence note.
- Quality gate: labels, legends, and selected points are readable from a
  presentation distance.

## Decision Table

- Purpose: compare options and justify the recommendation.
- Required inputs: options, metric values, risk/caveat, selected option, and
  approval constraints.
- Output shape: compact table with highlighted selection.
- Quality gate: selection is based on evidence and caveats, not aesthetics.

## Recommendation

- Purpose: tell the audience what should happen next.
- Required inputs: decision, expected evidence, required approval, and owner or
  timing if known.
- Output shape: one recommendation statement plus two or three supporting
  reasons.
- Quality gate: recommendation does not imply unapproved full training, Slurm,
  split, metric, or label changes.

## Limitations And Next Experiment

- Purpose: close honestly and make the next validation concrete.
- Required inputs: non-final status, major limitations, cheapest next check,
  and promotion rule.
- Output shape: use the `Conclusion` layout: caveat list plus next experiment
  card, recommendation, decision table, or phase plan.
- Quality gate: the final slide leaves the audience with a realistic action,
  not an overstated win.

## Appendix Slides

- Purpose: hold dense tables, extra methods, supplementary figures, and audit
  details.
- Required inputs: source context and why the detail may be needed.
- Output shape: dense but still labeled and readable support slides.
- Quality gate: appendix material does not leak into the primary live narrative
  unless it supports the main takeaway.
