# Reporting Guide

This guide is the canonical format for formal reports, presentation decks,
figures, curated experiment summaries, and publication-style artifacts created
from this template. It does not apply to quick chat summaries or temporary
notes.

## Required Before Creating Artifacts

- Read this guide before creating or updating a formal report, HTML summary,
  slide deck, figure set, tracked experiment summary, or publication-style
  artifact.
- Preserve the experiment policy: do not change final splits, metric
  definitions, label rules, or report selection criteria unless explicitly
  instructed.
- Keep raw outputs under ignored `experiments/` directories; keep generated
  reports, decks, and figure assets under `reports/` as local artifacts unless
  the user explicitly asks to track a specific curated output.

## Report Structure

Formal HTML or Markdown reports should include:

- title, run id, date, author/context, and repository commit when available
- executive summary with the decision or recommendation
- task formulation, data source, split policy, and target definition
- method descriptions with enough detail to reproduce the comparison
- primary metric and secondary metric definitions
- key tables and figures with clear lower-is-better or higher-is-better labels
- result interpretation, selected decision point, and rationale
- limitations, risks, approval requirements, and next recommended experiment

## Presentation Structure

Lab meeting decks and project-review presentations should use a concise
live-presentation flow:

- title and one-sentence takeaway
- objective and task formulation
- data/split summary
- method overview
- modeling, reconstruction, prediction, or evaluation protocol
- primary metric and supporting metrics
- key result curves
- decision table
- recommendation
- limitations and next experiment

Keep one main message per slide. Put dense tables, long feature lists, and
implementation details in the HTML report or appendix, not on primary
presentation slides.

## Visual Style

- Use WPI branding as the default visual theme for formal template artifacts:
  - Crimson: `#AC2B37`
  - Gray: `#A9B0B7`
  - Black: `#000000`
  - White or off-white backgrounds for readability
- Do not use a WPI logo unless an approved logo asset is provided.
- Use crimson for emphasis, decision markers, and selected curves. Use gray for
  rules, axes, secondary labels, and muted comparison elements.
- Figures must label units and directionality, for example `nRMSE (lower is
  better)` or `spatial correlation (higher is better)`.

## File Conventions

- Topic reports live under `reports/<topic>/` as generated artifacts.
- Reusable plot/table assets live under `reports/<topic>/assets/` as local
  generated artifacts.
- Formal HTML reports should be self-contained and portable as single files:
  embed required figures as `data:image/...;base64,...` data URIs.
- Keep source figure assets in `reports/<topic>/assets/` for reuse, even when
  they are embedded in HTML reports.
- Relative image links are allowed only for local drafts or explicitly
  multi-file report bundles.
- Curated summaries should use stable, reviewable names such as
  `reports/<topic>/<run_id>_summary.md`.
- Formal report bundles should use stable topic names such as
  `reports/<topic>/<topic>_report.html` and
  `reports/<topic>/<topic>_lab_meeting.pptx`.
- Raw experiment CSV/JSON outputs remain under ignored directories such as
  `experiments/<run_id>/` or `experiments/<topic>/<run_id>/`.
- Example-specific report conventions belong under `examples/<project>/docs/`
  and should point back to this guide.

## Required Caveats

Every exploratory report must explicitly state when results are not final test
metrics. State the evaluation split, metric status, baseline or model family,
and promotion requirements before making recommendations. Do not present
validation, proxy, smoke, or ablation results as final evaluation results unless
the experiment has been promoted to the final evaluation protocol.
