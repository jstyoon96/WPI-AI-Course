---
name: "research-reporting"
description: "Use when creating, reviewing, or converting formal ML research reports, HTML/Markdown summaries, lab meeting decks, PowerPoint/PPTX presentations, figure bundles, curated experiment summaries, or report-to-deck artifacts for this harness."
---

# Research Reporting

Use this skill for formal research artifacts, not quick chat summaries. Pair it
with `ml-research-harness` when the artifact discusses data, metrics, training,
evaluation, diagnostics, experiment selection, or next-run planning. Pair it
with the built-in `Presentations` skill when producing or editing PPTX decks.

## Source Rules

- Read `docs/REPORTING_GUIDE.md` before creating or updating a formal report,
  deck, figure bundle, or curated experiment summary.
- Preserve the harness policy: do not change final splits, metric definitions,
  label rules, report selection criteria, full-training behavior, or Slurm
  behavior unless the user explicitly approves that change.
- Treat experiment outputs as evidence, not decoration. Every claim must point
  to a run id, config, metric, table, figure, commit, or stated assumption.
- State when results are exploratory, validation-only, proxy, smoke, ablation,
  or otherwise not final test metrics.

## Workflow

1. Classify the artifact: formal report, HTML report, Markdown summary, lab
   meeting deck, report-to-deck conversion, figure bundle, or final QA review.
2. Gather inputs: topic, audience, run ids, configs, data/split status, metric
   definitions, figures/tables, commit, caveats, approval constraints, and next
   experiment candidates.
3. Choose the section playbook:
   - Reports: `references/report_sections.md`
   - Decks: `references/deck_sections.md`
   - Reusable prompts: `references/prompt_templates.md`
4. Apply the section quality contract to every section or slide:
   purpose, required inputs, output shape, quality gate, and failure action.
5. For decks, classify each slide as `first page`, `body`, or `conclusion`
   before authoring so the visual structure stays consistent.
6. Keep report and deck claims synchronized. Decks may be lighter and more
   visual, but they must not add stronger claims than the report supports.
7. Save generated artifacts under `reports/<topic>/` unless the user gives a
   different path. Keep reusable figure/table assets under
   `reports/<topic>/assets/`.

## Visual And Presentation Rules

- Use the WPI-light theme by default for formal template artifacts: crimson
  `#AC2B37`, gray `#A9B0B7`, black `#000000`, and white/off-white backgrounds.
- For decks, use the three-part WPI deck format in
  `references/deck_sections.md`: first page, body, and conclusion.
- Do not use a WPI logo unless an approved logo asset is provided.
- For decks, use assertion-style slide titles: the title states the takeaway,
  not just the topic.
- Keep one primary message per slide and one foreground evidence object where
  possible. Dense tables and implementation details belong in reports or
  appendices.
- PPTX output must remain editable and must pass rendered QA through the
  presentation runtime when a PPTX is actually generated.

## Quality Gates

Before delivering a formal artifact, verify:

- Claims match evidence and do not imply final-test status without approval.
- Split, metric, label, baseline/model family, and promotion status are stated.
- Metric direction is explicit, for example `lower is better` or
  `higher is better`.
- Limitations and next recommended experiment are present.
- Figures and tables have labels, units, captions, and readable text.
- Report sections and deck slides use consistent terminology and tone.

## External Principles To Apply

- OpenAI skills: keep the skill focused, concise, and reference-driven.
- MIT/Harvard scientific presentation guidance: one takeaway per slide, visual
  evidence over text, and titles that carry the story.
- NeurIPS checklist principles: honest scope, reproducibility, limitations, and
  evidence-backed claims.
