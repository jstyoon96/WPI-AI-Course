---
name: "course-material-authoring"
description: "Use when editing WPI AI Bootcamp public labs, notebooks, course docs, validation checks, or student-facing runtime instructions."
---

# Course Material Authoring

## Required Reading
Before editing public lab material, read the relevant files:

- `AGENTS.md`
- `README.md`
- `docs/COURSE_STRUCTURE.md`
- `docs/LAB_AUTHORING_GUIDE.md`
- `docs/LAB_PRODUCTION_WORKFLOW.md`
- `docs/NOTEBOOK_TEMPLATE_STANDARD.md`
- `docs/VISUAL_STYLE_GUIDE.md`
- `docs/DATA_SOURCE_POLICY.md`
- `docs/RUNTIME_GUIDE.md`
- `docs/CONTENT_REVIEW_CHECKLIST.md`
- `docs/ATTRIBUTION_AND_LICENSE.md`

## Safety Rules
- Keep completed answers and instructor-only notes out of public lab folders.
- Keep raw draft material out of public lab folders.
- Keep raw data files out of the repository; commit reusable loader code under
  `src/wpi_ai_bootcamp/data/`.
- Preserve visible `TODO` markers in student notebooks.
- Keep notebooks runnable in Google Colab unless a lab explicitly says otherwise.
- Use WPI visual style for notebook plots, diagrams, and explanatory images.
- Cite external datasets, code, images, and conceptual references.
- Keep generated notebook outputs small.

## Default Workflow
1. Inspect the target lab README, notebook, and relevant draft inputs.
2. Make one coherent student-facing change.
3. Run `python3 scripts/check_labs.py`.
4. Run `pytest tests/unit tests/smoke` when validation logic or package code changes.
5. Report changed files, checks run, results, risks, and next action.
