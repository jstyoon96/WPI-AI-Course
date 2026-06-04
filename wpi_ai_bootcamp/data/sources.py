"""Shared source metadata for lab data loaders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataSource:
    """Metadata needed to cite a lab dataset."""

    name: str
    loader: str
    url: str
    citation: str
    license_note: str


SOURCES = {
    "ecg_scipy": DataSource(
        name="SciPy electrocardiogram sample",
        loader="scipy.datasets.electrocardiogram",
        url="https://docs.scipy.org/doc/scipy/reference/generated/scipy.datasets.electrocardiogram.html",
        citation="SciPy ECG sample derived from MIT-BIH Arrhythmia Database record 208 on PhysioNet.",
        license_note="Review SciPy and PhysioNet terms before public release notes are finalized.",
    ),
    "skimage_sample": DataSource(
        name="scikit-image sample image",
        loader="skimage.data",
        url="https://scikit-image.org/docs/stable/api/skimage.data.html",
        citation="scikit-image sample data.",
        license_note="Review the selected scikit-image sample attribution before release.",
    ),
    "skimage_retina": DataSource(
        name="scikit-image retina sample image",
        loader="skimage.data.retina",
        url="https://scikit-image.org/docs/stable/api/skimage.data.html",
        citation="scikit-image retina sample data.",
        license_note="Review scikit-image sample data terms before public course release.",
    ),
    "bbbc038_nuclei": DataSource(
        name="BBBC038 2018 Data Science Bowl nuclei segmentation dataset",
        loader="wpi_ai_bootcamp.data.load_bbbc038_nuclei_segmentation_subset",
        url="https://bbbc.broadinstitute.org/BBBC038",
        citation=(
            "Caicedo, J. C., Goodman, A., Karhohs, K. W. et al. Nucleus "
            "segmentation across imaging experiments: the 2018 Data Science "
            "Bowl. Nature Methods 16, 1247-1253 (2019)."
        ),
        license_note=(
            "BBBC038 page lists the image set copyright as CC0. Students should "
            "cite BBBC038 and the Nature Methods paper when reusing the data."
        ),
    ),
}


def describe_source(source_id: str) -> DataSource:
    """Return citation metadata for a known source."""

    return SOURCES[source_id]
