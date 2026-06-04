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


def load_oxford_pet_segmentation_subset(
    root: str | None = None,
    split: str = "trainval",
    max_samples: int = 96,
    image_size: int = 128,
    binary_foreground: bool = True,
    download: bool = True,
    random_state: int = 42,
):
    """Load a compact Oxford-IIIT Pet image segmentation subset.

    The helper downloads data through ``torchvision`` at runtime and returns a
    small NumPy subset suitable for Colab teaching notebooks. No raw dataset
    files are stored in the course repository.
    """

    from pathlib import Path
    from tempfile import gettempdir

    import numpy as np
    from PIL import Image
    from torchvision.datasets import OxfordIIITPet

    if split not in {"trainval", "test"}:
        raise ValueError("split must be 'trainval' or 'test'")
    if max_samples <= 0:
        raise ValueError("max_samples must be positive")
    if image_size <= 0:
        raise ValueError("image_size must be positive")

    data_root = Path(root) if root is not None else Path(gettempdir()) / "wpi_ai_bootcamp_data"
    dataset = OxfordIIITPet(
        root=str(data_root),
        split=split,
        target_types="segmentation",
        download=download,
    )

    sample_count = min(max_samples, len(dataset))
    rng = np.random.default_rng(random_state)
    selected_indices = np.sort(rng.choice(len(dataset), size=sample_count, replace=False))

    images = []
    masks = []
    for idx in selected_indices:
        image, trimap = dataset[int(idx)]
        image = image.convert("L").resize((image_size, image_size), Image.BILINEAR)
        trimap = trimap.resize((image_size, image_size), Image.NEAREST)

        image_array = np.asarray(image, dtype=np.float32) / 255.0
        trimap_array = np.asarray(trimap, dtype=np.uint8)
        if binary_foreground:
            mask_array = (trimap_array == 1).astype(np.float32)
        else:
            mask_array = trimap_array.astype(np.float32)

        images.append(image_array[np.newaxis, ...])
        masks.append(mask_array[np.newaxis, ...])

    source = describe_source("oxford_iiit_pet")
    metadata = {
        "source": source,
        "split": split,
        "image_size": int(image_size),
        "selected_indices": selected_indices.astype(int).tolist(),
        "binary_foreground": bool(binary_foreground),
        "torchvision_docs": (
            "https://docs.pytorch.org/vision/main/generated/"
            "torchvision.datasets.OxfordIIITPet.html"
        ),
    }
    return (
        np.stack(images).astype(np.float32),
        np.stack(masks).astype(np.float32),
        metadata,
    )
