# Visual Style Guide

## Purpose
All public lab plots, diagrams, and explanatory images should feel consistent
with WPI course material while remaining readable in Google Colab and GitHub.

## Official Color Tokens
Use the WPI institutional colors as the base palette:

- WPI Crimson: `#AC2B37`
- WPI Gray: `#A9B0B7`
- Black: `#000000`
- White: `#FFFFFF`

The course helper package exposes these values through:

```python
from wpi_ai_bootcamp.style import WPI_COLORS, apply_wpi_plot_style

apply_wpi_plot_style()
```

## Plot Rules
- Use WPI Crimson for the primary signal, model, region, or result.
- Use WPI Gray for baselines, reference lines, uncertainty bands, and inactive
  context.
- Use black or dark gray for labels, axes, and high-contrast annotations.
- Use the secondary accent colors from `wpi_ai_bootcamp.style` only when a
  figure needs more than three clearly distinct series.
- Avoid default rainbow colormaps unless the data is naturally continuous and
  the chosen map is explained.
- Keep figure outputs small enough for GitHub review.

## Notebook Rule
Every public notebook setup section should import or define the WPI style and
call `apply_wpi_plot_style()` before plotting. If the package is not installed
in Colab yet, use the fallback style code from `templates/lab/notebook.ipynb`.

## Diagram And Image Rules
- Prefer WPI Crimson for highlights and arrows.
- Prefer neutral gray backgrounds and borders.
- Do not use decorative colors that compete with the learning signal.
- Cite external diagrams or images in the lab attribution section.

## Source
Color values come from the
[WPI Institutional Guidelines](https://www.wpi.edu/sites/default/files/2023-11/WPI_Institutional_Guidelines.pdf),
which identify Crimson PMS 187c as `#AC2B37`, Gray PMS 429c as `#A9B0B7`,
and Black as `#000000`.
