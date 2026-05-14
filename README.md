# WPI AI Bootcamp Lab Materials

Student-facing notebook labs for a WPI AI bootcamp. The repository is organized
by week, with two Colab labs per week and shared data-loading utilities for
notebooks.

## Labs

| Week | Folder | Lab 1 | Lab 2 |
| --- | --- | --- | --- |
| 1 | [WPI_week1](WPI_week1) | Biomedical Imaging | Biomedical Signals |
| 2 | [WPI_week2](WPI_week2) | Topic placeholder | Topic placeholder |
| 3 | [WPI_week3](WPI_week3) | Topic placeholder | Topic placeholder |
| 4 | [WPI_week4](WPI_week4) | Topic placeholder | Topic placeholder |

Each week folder contains `lab1/` and `lab2/`, and each lab contains a matching
notebook such as `WPI_week1_lab1.ipynb`.

## Running In Colab

1. Open the week folder for the lab you want.
2. Open `lab1/` or `lab2/`.
3. Open the matching notebook and use the Colab badge.
4. Choose a GPU runtime only when the lab asks for it.
5. Work through the notebook cells and complete every `TODO`.

Colab is the official student runtime for the first version of the course.

## Data Loading

Large data files are not committed to this repository. Shared loader code lives
under `src/wpi_ai_bootcamp/data/`, while local raw data folders remain ignored.
Notebooks should call loader functions such as `load_ecg_signal()` or
`load_imaging_sample()` when a shared dataset is useful.

## Creating Weekly Labs

Local source drafts go under `draft/` and are ignored by git. Public labs are
created from templates:

```bash
python3 scripts/create_lab_scaffold.py --week 1 --lab 1 --title "Biomedical Imaging"
python3 scripts/check_labs.py
```

See [docs/LAB_PRODUCTION_WORKFLOW.md](docs/LAB_PRODUCTION_WORKFLOW.md),
[docs/NOTEBOOK_TEMPLATE_STANDARD.md](docs/NOTEBOOK_TEMPLATE_STANDARD.md), and
[docs/DATA_SOURCE_POLICY.md](docs/DATA_SOURCE_POLICY.md).

## Instructor Materials

Slides, completed answers, review notes, and raw drafts are local working
materials. Keep them in `instructor/` or `draft/`; both folders are ignored by
git.

## Validation

Run the lightweight checks before publishing lab changes:

```bash
python3 scripts/check_labs.py
pytest tests/unit tests/smoke
```

## Attribution And License

External datasets, images, snippets, and references must be cited before public
release. MIT Introduction to Deep Learning is a structural reference only; do
not copy its lab content without license review and attribution. See
[docs/ATTRIBUTION_AND_LICENSE.md](docs/ATTRIBUTION_AND_LICENSE.md).
