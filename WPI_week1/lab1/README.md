# Biomedical Imaging: Deterministic Segmentation Baseline

## Learning Objectives
- Treat a biomedical image as structured numerical data.
- Normalize image intensities before threshold-based segmentation.
- Build a simple deterministic segmentation baseline with thresholding and
  morphology.
- Create a WPI-styled overlay for visual quality control.
- Produce a small structured output table from the mask.

## Estimated Time
90-120 minutes.

## Prerequisites
- Basic Python syntax
- NumPy array indexing
- Basic plotting with Matplotlib
- A Google account for Colab

## Colab Link
Open `WPI_week1_lab1.ipynb` in Google Colab from this repository once the public
GitHub URL is finalized.

## Files In This Lab
- `WPI_week1_lab1.ipynb`: student notebook
- `img/`: public images used by the lab

## Graded Deliverables
This lab is graded out of `100 pts`.

- Completed Colab notebook with generated plots and tables: `60 pts`
- Word response document: `40 pts`

Name the Word file:

```text
WPI_week1_lab1_responses_LastName_FirstName.docx
```

The Word document should include Q1-Q5 in 2-5 sentences each. Keep longer
written responses in the Word document rather than in the notebook.

## Data Source
This lab uses sample image data from `skimage.data`. No image data file is
committed to this repository. The notebook first tries the shared
`wpi_ai_bootcamp.data` loader and then falls back to `skimage.data` directly in
Colab.

## Submission Or Check Instructions
Complete every visible `TODO` in the notebook. The completed notebook should
contain the requested plots, the structured output DataFrame, and short written
notes where requested. Submit the completed notebook and the Word response
document.

## Clinical Disclaimer
The `risk_score`, `alarm`, `quality`, and `review_flag` values in this lab are
synthetic teaching outputs. They are designed for workflow practice and are not
clinically validated measurements.

## Attribution
This lab uses scikit-image sample data and Python scientific computing
libraries. Review final source and license notes before public course release.
