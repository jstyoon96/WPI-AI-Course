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
    "oxford_iiit_pet": DataSource(
        name="Oxford-IIIT Pet segmentation dataset",
        loader="torchvision.datasets.OxfordIIITPet",
        url="https://www.robots.ox.ac.uk/~vgg/data/pets/",
        citation=(
            "O. M. Parkhi, A. Vedaldi, A. Zisserman, and C. V. Jawahar, "
            "Cats and Dogs, IEEE Conference on Computer Vision and Pattern "
            "Recognition, 2012."
        ),
        license_note=(
            "Dataset page lists Creative Commons Attribution-ShareAlike 4.0 "
            "International for commercial/research download; image copyrights "
            "remain with original owners."
        ),
    ),
}


def describe_source(source_id: str) -> DataSource:
    """Return citation metadata for a known source."""

    return SOURCES[source_id]
