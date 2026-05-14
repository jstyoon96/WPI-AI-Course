# Data Source Policy

## Core Rule
Data files are not committed by default. Data loading code is committed under
`src/wpi_ai_bootcamp/data/`.

## Priority Order
1. Library-provided data available in the default Colab environment or through a
   lightweight install.
2. Stable public downloadable data with clear citation and license.
3. Small repository sample data, only when needed for reproducibility and after
   explicit review.

## Do Not Commit
- Large datasets
- Private data
- Root `data/` folders
- Raw draft data unless explicitly approved for public release
- Files without clear source or licensing information

## Loader Code
Shared loader functions should live in `src/wpi_ai_bootcamp/data/` so notebooks
can stay short and consistent. Loader docstrings or source metadata should name
the source, loader, URL, citation, and license note.

## Review Questions
- Can students load the data in Colab without local setup?
- Is the data small enough for repeated class use?
- Is the source stable?
- Is the license compatible with public course material?
- Is attribution included in the README or notebook?
- Should a reusable loader be added or updated?

## Week 1 Candidate Sources
- Signals: `scipy.datasets.electrocardiogram()`
- Imaging: `skimage.data` biomedical or general image examples, subject to
  lab-specific review
