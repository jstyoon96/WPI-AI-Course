---
name: "draft-to-lab-conversion"
description: "Use when converting weekly draft materials in draft/Week N_* into public WPI_weekN/labM Colab notebook labs while excluding slides and private source files."
---

# Draft To Lab Conversion

## Purpose
Convert local weekly drafts into public student-facing lab materials.

## Required Reading
- `docs/LAB_PRODUCTION_WORKFLOW.md`
- `docs/LAB_AUTHORING_GUIDE.md`
- `docs/NOTEBOOK_TEMPLATE_STANDARD.md`
- `docs/DATA_SOURCE_POLICY.md`

## Workflow
1. Inventory the target `draft/Week N_*` folder.
2. Classify files as source notes, source notebook, data candidate, slide deck,
   or private review material.
3. Ignore slide decks unless the user explicitly asks for slide work.
4. Extract learning goals, activities, constraints, and data needs.
5. Convert platform-specific instructions to Python and Google Colab.
6. Create or update `WPI_weekN/labM/` using the lab scaffold template.
7. Decide whether shared data loading code belongs under `src/wpi_ai_bootcamp/data/`.
8. Keep completed answers, raw draft files, and private notes out of public lab
   folders.

## Output Contract
Return the target lab folder, source files inspected, conversion decisions, data
choice, and remaining authoring gaps.
