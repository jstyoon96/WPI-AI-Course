"""Image data loaders for WPI AI Bootcamp notebooks."""

from __future__ import annotations

from .sources import describe_source


def load_imaging_sample(name: str = "retina"):
    """Load a small public image sample for Colab notebooks.

    Parameters
    ----------
    name:
        Name of a ``skimage.data`` loader. Defaults to ``retina``.

    Returns
    -------
    tuple
        ``(image, source)`` where ``image`` is the loaded sample and ``source``
        contains citation metadata.
    """

    from skimage import data

    if not hasattr(data, name):
        raise ValueError(f"unknown skimage.data sample: {name}")
    image = getattr(data, name)()
    source_id = "skimage_retina" if name == "retina" else "skimage_sample"
    return image, describe_source(source_id)
