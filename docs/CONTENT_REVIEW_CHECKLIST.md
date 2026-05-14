# Content Review Checklist

Use this checklist before publishing lab updates.

## Student Experience
- The lab has clear learning objectives.
- The estimated time is realistic.
- The notebook starts with Colab guidance.
- Every coding exercise has a visible `TODO`.
- Reflection questions check conceptual understanding.
- The lab shows a `100 pts` total.
- Part-level questions and point values are visible to students.
- Word response document instructions are clear.
- Plots and explanatory figures follow the WPI visual style.

## Technical Quality
- The path follows `WPI_week{n}/lab{m}`.
- The notebook filename matches `WPI_week{n}_lab{m}.ipynb`.
- The notebook parses as valid JSON.
- Setup cells do not require local-only paths.
- Outputs are small enough for GitHub review.
- Notebook setup applies `apply_wpi_plot_style()` or equivalent WPI style
  fallback.
- The visible rubric sums to `100 pts`.
- Public lab files do not contain secrets or private paths.
- Validation passes with `python3 scripts/check_labs.py`.

## Public/Private Boundary
- No completed answer notebooks are present in public lab folders.
- No answer keys or instructor-only notes are present in public lab folders.
- Raw draft files remain under local `draft/`.
- Slides and completed answer files remain under local `instructor/`.
- Root `data/` files are not staged; shared loader code belongs under
  `src/wpi_ai_bootcamp/data/`.

## Attribution
- External datasets, images, code snippets, and conceptual references are cited.
- MIT materials are used only as structural reference unless separately
  reviewed for license and attribution.
