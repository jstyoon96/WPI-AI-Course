# Notebook Template Standard

Every public notebook should follow this cell order unless the instructor
explicitly requests a different structure.

## Required Cell Order
1. Colab badge, title, audience, and estimated time
2. Learning objectives
3. Grading and Word response submission instructions
4. Setup instructions
5. Setup code cell with WPI visual style
6. Data loading explanation
7. Data loading code cell, preferably using `wpi_ai_bootcamp.data`
8. Concept explanation
9. Guided code cell
10. Student `TODO`
11. Part-level assessment block with points, required output, Word response
    prompt, and grading criteria
12. Optional challenge
13. Attribution

## Markdown Style
- Keep each explanation short and close to the code it supports.
- Define terms before asking students to use them.
- Use checkpoint questions to connect output to concepts.
- Avoid long lecture notes inside notebooks.
- Keep point values visible near the work they evaluate.

## Code Style
- Prefer small, runnable cells.
- Avoid local absolute paths.
- Keep outputs small.
- Add package installs only when Colab does not already provide the package.
- Preserve visible `TODO` markers in student-facing exercises.
- Prefer shared data loaders over repeated download code.

## Assessment Style
- Every lab must show `100 pts` total.
- Default split: notebook execution and artifacts `60 pts`, Word response
  document `40 pts`.
- Default part structure: five parts, each worth `20 pts`.
- Each part should identify the required notebook output and the corresponding
  Word response question.
- Word response file naming should follow
  `WPI_week{n}_lab{m}_responses_LastName_FirstName.docx`.
- Do not include model responses or private grading notes in public notebooks.

## Visual Style
- Setup cells must call `apply_wpi_plot_style()` or include the template
  fallback before any plotting.
- Use `WPI_COLORS["crimson"]` for the main result or signal in a figure.
- Use WPI gray or neutral grays for baselines, axes, context, and secondary
  annotations.
- Follow `docs/VISUAL_STYLE_GUIDE.md` for plots, diagrams, and lab images.
