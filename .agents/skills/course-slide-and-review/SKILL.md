---
name: "course-slide-and-review"
description: "Use when drafting, reviewing, or structuring WPI AI Bootcamp slides, instructor notes, lab release reviews, or student-facing summaries."
---

# Course Slide And Review

## Source Rules
- Public lab materials use `WPI_week{n}/lab{m}/` folders.
- Slides, completed answers, and instructor review notes live under local
  `instructor/` and are not committed.
- Raw weekly source material lives under local `draft/` and is not committed.
- If a public README or notebook references external material, include
  attribution.

## Workflow
1. Identify whether the artifact is public student material or instructor-only.
2. For public material, check clarity, Colab readiness, TODO markers, and
   attribution.
3. For instructor material, keep it under `instructor/` and do not stage it.
4. Run `python3 scripts/check_labs.py` before public lab release.

## Quality Gates
- The learning objective is clear.
- The activity fits the estimated time.
- Students can start from Colab without local setup.
- The public artifact does not reveal completed answers.
- Attribution is visible where needed.
