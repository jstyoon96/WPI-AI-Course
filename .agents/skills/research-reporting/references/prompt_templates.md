# Prompt Templates

These templates are starting prompts for repeatable reporting work. Fill the
bracketed fields before use. Keep claims evidence-backed and preserve the
harness policy.

## Formal Report

```text
$research-reporting
Create a formal [HTML/Markdown] report for [topic].

Inputs:
- run ids: [run ids or "none yet"]
- configs: [config paths]
- commit: [commit hash if available]
- data/split status: [train/val/test/proxy/final status]
- metrics: [primary and secondary metrics with direction]
- figures/tables: [paths or descriptions]
- audience: [lab/project review/paper planning/etc.]
- caveats: [known limitations and approval constraints]

Requirements:
- Follow docs/REPORTING_GUIDE.md and references/report_sections.md.
- Include evidence, caveats, limitations, QA status, and next recommended
  experiment.
- Do not imply final-test performance unless explicitly supported.
- Save under reports/[topic]/ using stable names unless told otherwise.
```

## Lab Meeting PPT

```text
$research-reporting
Create a WPI-light lab meeting PPTX deck for [topic].

Inputs:
- source report or notes: [path or summary]
- run ids/configs: [run ids and configs]
- audience and time budget: [audience, minutes]
- key evidence: [figures/tables/metrics]
- caveats: [non-final/proxy/validation/smoke/ablation status]
- desired output path: reports/[topic]/[topic]_lab_meeting.pptx

Requirements:
- Pair with the Presentations skill for PPTX authoring and rendered QA.
- Follow references/deck_sections.md.
- Use the three-part WPI deck format: first page, body slides, conclusion.
- Include evidence, caveats, section QA status, and next recommended step.
- Use one assertion-style takeaway per slide.
- Use WPI crimson/gray/black/white theme, but no WPI logo unless an approved
  logo asset is provided.
- Keep dense details in appendix or the report.
```

## Report To Deck Conversion

```text
$research-reporting
Convert [report path] into a concise lab meeting deck.

Requirements:
- Preserve the report's scientific claims and caveats.
- Do not introduce stronger claims than the report supports.
- Convert each major report section into the smallest useful slide sequence.
- Classify each slide as first page, body, or conclusion before authoring.
- Include evidence, caveats, slide QA status, and next recommended step.
- Use the deck section playbook and run final slide QA.
- Output to reports/[topic]/[topic]_lab_meeting.pptx.
```

## Figure And Table QA

```text
$research-reporting
Review the figures and tables for [report/deck path or topic].

Check:
- metric names, units, and directionality
- axis labels, legends, selected points, and captions
- run id/config/source traceability
- split/label/metric caveats
- readability in report and presentation contexts

Return:
- blocking issues
- non-blocking polish suggestions
- exact fixes needed before publication or presentation
- evidence, caveat, QA, and next-step status for each blocking issue
```

## Final Artifact Review

```text
$research-reporting
Perform a final QA review for [artifact path].

Check:
- every claim has evidence or is marked as an assumption
- final/proxy/validation/smoke status is explicit
- split, metric, and label rules are not silently changed
- every report section or slide passes its section quality gate
- limitations, risks, and next recommended step are present
- WPI-light visual rules are applied consistently

Return:
- pass/fail
- blocking issues
- suggested edits
- remaining risks
- evidence, caveat, QA, and next recommended step
```
