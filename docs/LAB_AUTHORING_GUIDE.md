# Lab Authoring Guide

## Audience
Write for mixed-level learners. Assume students know basic Python syntax, but
do not assume prior machine-learning or deep-learning experience.

## Naming Rule
Every public lab uses:

```text
WPI_week{week_number}/lab{lab_number}/WPI_week{week_number}_lab{lab_number}.ipynb
```

Example: week folder `WPI_week1`, lab folder `lab1`, notebook
`WPI_week1_lab1.ipynb`.

## Draft Intake
Weekly raw material goes under `draft/Week N_*`. Treat draft files as local
inputs, not public student material. Slides are out of scope for lab conversion
unless the user explicitly asks to work on them.

When converting draft material:

- Extract learning goals, activities, and required data.
- Rewrite platform-specific instructions for Python and Google Colab.
- Decide whether a shared loader belongs in `src/wpi_ai_bootcamp/data/`.
- Keep student notebooks public and completed answers private.
- Record external data and image sources for attribution.

## Required Lab README Sections
Each lab README should include:

- Learning objectives
- Estimated time
- Prerequisites
- Colab link or Colab opening instructions
- Files in this lab
- Graded deliverables and the `100 pts` total
- Submission or check instructions
- Attribution

## Required Notebook Shape
Each student notebook should include:

- Colab badge
- Lab title, audience, and estimated time
- Learning objectives
- Setup cell
- WPI visual style setup using `wpi_ai_bootcamp.style` or the notebook template
  fallback
- Data loading cell, preferably using `wpi_ai_bootcamp.data`
- Concept markdown before each activity
- Guided code cells
- Visible `TODO` cells
- Part-level point values and required outputs
- Word response questions
- Checkpoint or reflection questions
- Optional challenge
- Attribution cell

## Assessment Rule
Every public lab is worth `100 pts`.

The default structure is:

- Notebook execution and artifacts: `60 pts`
- Word response document: `40 pts`

Use five parts by default. Each part is `20 pts`: `12 pts` for the notebook
artifact and `8 pts` for the corresponding Word response question. If a future
lab needs a different number of parts, the visible rubric must still sum to
`100 pts`.

Word response files should use:

```text
WPI_week{week_number}_lab{lab_number}_responses_LastName_FirstName.docx
```

Public labs may include questions, point values, and grading criteria. Do not
include model responses or private grading notes.

## Data Source Rule
Prefer library-provided or public downloadable datasets that work directly in
Colab. Do not commit large datasets. Small sample files may be included only
after checking size, license, and reproducibility.

## Visual Style Rule
Use WPI colors for public lab plots and explanatory figures. The primary
result should usually be WPI Crimson, reference or background information
should use WPI Gray or neutral grays, and all notebooks should apply
`apply_wpi_plot_style()` in setup. See `docs/VISUAL_STYLE_GUIDE.md`.

## Public/Private Boundary
Student labs must not include completed notebooks, answer keys, hidden
instructor notes, private grading rubrics, or raw draft material. Keep those in
`instructor/` or `draft/`.
