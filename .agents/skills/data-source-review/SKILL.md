---
name: "data-source-review"
description: "Use when deciding whether lab data should come from library datasets, public downloads, shared loader code under src/wpi_ai_bootcamp/data, or small reviewed repo samples."
---

# Data Source Review

## Required Reading
- `docs/DATA_SOURCE_POLICY.md`
- `docs/VISUAL_STYLE_GUIDE.md`
- `docs/ATTRIBUTION_AND_LICENSE.md`
- `src/wpi_ai_bootcamp/data/`

## Priority
1. Library-provided data that works in Colab.
2. Stable public downloadable data with citation and license.
3. Small repository sample data when required for reproducibility.

## Reject Or Escalate
- Large data files for GitHub.
- Root `data/` files.
- Private data.
- Raw draft data without explicit approval for public release.
- Sources without clear license or attribution.

## Output Contract
State the chosen source, why it fits Colab, license/citation notes, whether a
loader should be added under `src/wpi_ai_bootcamp/data/`, and whether any file
should be committed. For data that will be plotted, note any visualization
constraints such as categorical labels, color accessibility, or image contrast.
