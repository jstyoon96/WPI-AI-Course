# Lab Production Workflow

## Purpose
Use this workflow whenever a new weekly draft is added and needs to become a
public Colab notebook lab.

## Steps
1. Inventory `draft/Week N_*` and classify files as source notes, source
   notebooks, data candidates, slide decks, or private review material.
2. Ignore slides unless the current task explicitly asks for slide work.
3. Create or refresh the public scaffold:
   ```bash
   python3 scripts/create_lab_scaffold.py --week N --lab M --title "Title"
   ```
4. Choose data using `docs/DATA_SOURCE_POLICY.md`.
5. Add or update a reusable loader under `src/wpi_ai_bootcamp/data/` when the
   dataset will be reused or the loading code is too long for a notebook cell.
6. Apply WPI visual rules from `docs/VISUAL_STYLE_GUIDE.md`; update shared
   style helpers only when a course-wide plotting rule is missing.
7. Write the notebook using `docs/NOTEBOOK_TEMPLATE_STANDARD.md`.
8. Update the lab README with objectives, prerequisites, runtime notes, and
   attribution.
9. Run:
   ```bash
   python3 scripts/check_labs.py
   pytest tests/unit tests/smoke
   ```
10. Confirm `draft/`, `instructor/`, and root `data/` files are not staged.

## Week 1 Mapping
- `WPI_week1/lab1`: Biomedical Imaging
- `WPI_week1/lab2`: Biomedical Signals
