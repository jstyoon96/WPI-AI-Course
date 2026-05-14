---
name: "cautious-coding"
description: "Use for small, careful implementation changes in this course-material repository."
---

# Cautious Coding

## Before Coding
- Read the files you will edit.
- Check whether the change affects public labs, private instructor materials, or
  validation logic.
- Preserve user work and avoid unrelated refactors.

## Simplicity First
- Prefer the smallest clear implementation.
- Keep notebooks and checks easy for future course staff to inspect.
- Avoid adding dependencies unless the course material needs them.

## Validation
- Run `python3 scripts/check_labs.py` after public lab changes.
- Run `pytest tests/unit tests/smoke` after Python or hook changes.
- Report any skipped checks with the reason.
