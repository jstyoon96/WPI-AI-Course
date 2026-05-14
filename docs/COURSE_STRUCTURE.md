# Course Structure

## Purpose
This repository hosts public student-facing notebook labs for a WPI AI
Bootcamp. It also contains templates, validation utilities, and shared data
loader code for producing the same lab format each week.

## Public Repository Layout
```text
README.md
docs/
templates/
WPI_week1/
  README.md
  lab1/
  lab2/
WPI_week2/
WPI_week3/
WPI_week4/
src/wpi_ai_bootcamp/
  data/
  style/
scripts/
tests/
```

## Week And Lab Naming
Use this exact public structure:

```text
WPI_week{week_number}/lab{lab_number}/WPI_week{week_number}_lab{lab_number}.ipynb
```

Each week has two labs by default. The initial course scaffold covers Week 1-4.

## Lab Layout
Each public lab folder contains:

- `README.md`: student-facing overview and run instructions.
- `WPI_week{week}_lab{lab}.ipynb`: the student notebook.
- `img/README.md`: placeholder for public images used by the lab.

## Data Loader Package
`src/wpi_ai_bootcamp/data/` stores code for loading public or
library-provided data in notebooks. It must not store large datasets. Root
`data/` remains ignored for local data files.

## Visual Style Package
`src/wpi_ai_bootcamp/style/` stores WPI color tokens and matplotlib defaults for
notebook plots. Student notebooks should apply this style in setup and follow
`docs/VISUAL_STYLE_GUIDE.md`.

## Local-Only Inputs
- `draft/`: raw weekly drafts, source notebooks, docx files, sample data, and
  other conversion inputs.
- `instructor/`: slides, completed answers, review notes, and private teaching
  materials.

Both folders are ignored by git.
