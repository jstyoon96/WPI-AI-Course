---
name: "lab-release-review"
description: "Use before publishing WPI AI Bootcamp labs to verify naming, README, notebook parse, Colab guidance, WPI visual style, TODO markers, no answer exposure, no draft exposure, and attribution."
---

# Lab Release Review

## Required Reading
- `docs/CONTENT_REVIEW_CHECKLIST.md`
- `docs/LAB_PRODUCTION_WORKFLOW.md`

## Checklist
- Path follows `WPI_week{n}/lab{m}`.
- Notebook filename matches folder name.
- README exists and has objectives, runtime notes, and attribution.
- Notebook parses as JSON.
- Colab guidance exists.
- Notebook setup applies WPI visual style.
- Visible `TODO` markers remain.
- Public lab folder has no completed answers, keys, instructor notes, or raw
  draft material.
- `draft/`, `instructor/`, and root `data/` are ignored.
- Shared data loading code, if needed, lives under `src/wpi_ai_bootcamp/data/`.

## Required Checks
```bash
python3 scripts/check_labs.py
pytest tests/unit tests/smoke
```
