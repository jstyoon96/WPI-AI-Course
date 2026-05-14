---
name: "colab-notebook-authoring"
description: "Use when creating or revising WPI AI Bootcamp student notebooks with the required Colab cell structure, markdown guidance, TODO cells, checkpoints, and attribution."
---

# Colab Notebook Authoring

## Required Reading
- `docs/NOTEBOOK_TEMPLATE_STANDARD.md`
- `docs/LAB_AUTHORING_GUIDE.md`
- `docs/VISUAL_STYLE_GUIDE.md`
- `templates/lab/notebook.ipynb`
- `src/wpi_ai_bootcamp/data/`

## Cell Order
1. Colab badge, title, audience, and estimated time
2. Learning objectives
3. Setup instructions
4. Setup code cell with WPI visual style
5. Data loading explanation
6. Data loading code cell, preferably using `wpi_ai_bootcamp.data`
7. Concept explanation
8. Guided code cell
9. Student `TODO`
10. Checkpoint or reflection prompt
11. Optional challenge
12. Attribution

## Rules
- Keep explanations close to the code they support.
- Use small runnable cells.
- Preserve visible `TODO` markers.
- Avoid local absolute paths.
- Keep outputs small for GitHub review.
- Prefer shared data loaders over repeated download code.
- Call `apply_wpi_plot_style()` before plotting and use WPI Crimson for primary
  results.
