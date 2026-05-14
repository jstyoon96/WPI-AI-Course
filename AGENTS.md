# AGENTS.md

## Role
You are assisting with WPI AI Bootcamp lab material development.

The repository contains public student-facing labs, lightweight validation
utilities, and gitignored instructor-only course assets. The audience is mixed:
students are expected to know basic Python, but may be new to machine learning
and deep learning.

## Required Reading Before Edits
Read the relevant files before making course material changes:

- `README.md`
- `docs/COURSE_STRUCTURE.md`
- `docs/LAB_AUTHORING_GUIDE.md`
- `docs/LAB_PRODUCTION_WORKFLOW.md`
- `docs/NOTEBOOK_TEMPLATE_STANDARD.md`
- `docs/DATA_SOURCE_POLICY.md`
- `docs/RUNTIME_GUIDE.md`
- `docs/CONTENT_REVIEW_CHECKLIST.md`
- `docs/ATTRIBUTION_AND_LICENSE.md`

## Non-Negotiable Rules
- Do not put answer notebooks, answer keys, or instructor-only notes in public
  lab folders.
- Do not commit files under `instructor/`.
- Do not commit files under `draft/`.
- Keep public notebooks runnable in Google Colab unless a lab explicitly states
  otherwise.
- Keep visible `TODO` markers in student notebooks.
- Do not copy third-party course text, images, notebooks, or slides without
  attribution and license review.
- Do not print, store, or commit secrets, SSH keys, passwords, tokens, or API
  keys.
- Prefer small, reviewable changes.

## Required Workflow
1. Inspect the relevant lab README, notebook, and docs.
2. Make one coherent course-material change.
3. Run the lightweight validation checks.
4. Summarize changed files, checks run, results, risks, and next action.

## Required Checks
Run as applicable:

```bash
python3 scripts/check_labs.py
pytest tests/unit tests/smoke
```

## Instructor-Only Materials
Use local `instructor/` folders for slides, answer notebooks, and review notes.
Use local `draft/` folders for raw weekly source material. Both folders are
intentionally gitignored.
