"""Image data loaders for WPI AI Bootcamp notebooks."""

from __future__ import annotations

from .sources import describe_source


BBBC038_STAGE1_TRAIN_URL = "https://data.broadinstitute.org/bbbc/BBBC038/stage1_train.zip"


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


def load_bbbc038_nuclei_segmentation_subset(
    root: str | None = None,
    max_samples: int = 128,
    image_size: int = 128,
    download: bool = True,
    random_state: int = 42,
    source_url: str = BBBC038_STAGE1_TRAIN_URL,
):
    """Load a compact BBBC038 nuclei segmentation subset for Colab.

    The loader downloads the public BBBC038 ``stage1_train.zip`` archive at
    runtime, reads microscopy image PNGs and per-nucleus mask PNGs, and merges
    the individual instance masks into one binary foreground mask per image.
    No raw data files are stored in the course repository.
    """

    from pathlib import Path
    from tempfile import gettempdir
    from urllib.request import urlretrieve
    from zipfile import ZipFile

    import numpy as np
    from PIL import Image

    if max_samples <= 0:
        raise ValueError("max_samples must be positive")
    if image_size <= 0:
        raise ValueError("image_size must be positive")

    data_root = Path(root) if root is not None else Path(gettempdir()) / "wpi_ai_bootcamp_data"
    data_root.mkdir(parents=True, exist_ok=True)
    archive_path = data_root / "bbbc038_stage1_train.zip"
    extract_dir = data_root / "bbbc038_stage1_train"

    if download and not archive_path.exists():
        urlretrieve(source_url, archive_path)
    if not archive_path.exists():
        raise FileNotFoundError(
            f"BBBC038 archive not found at {archive_path}. Set download=True or provide a cached archive."
        )

    if not extract_dir.exists():
        with ZipFile(archive_path) as archive:
            archive.extractall(extract_dir)

    case_dirs = sorted(path for path in extract_dir.rglob("*") if (path / "images").is_dir() and (path / "masks").is_dir())
    if not case_dirs:
        raise FileNotFoundError("No BBBC038 image/mask case folders were found after extraction.")

    sample_count = min(max_samples, len(case_dirs))
    rng = np.random.default_rng(random_state)
    selected_positions = np.sort(rng.choice(len(case_dirs), size=sample_count, replace=False))
    selected_dirs = [case_dirs[int(pos)] for pos in selected_positions]

    images = []
    masks = []
    case_ids = []
    for case_dir in selected_dirs:
        image_files = sorted((case_dir / "images").glob("*.png"))
        mask_files = sorted((case_dir / "masks").glob("*.png"))
        if not image_files or not mask_files:
            continue

        image = Image.open(image_files[0]).convert("L").resize((image_size, image_size), Image.BILINEAR)
        image_array = np.asarray(image, dtype=np.float32) / 255.0

        merged_mask = np.zeros((image_size, image_size), dtype=bool)
        for mask_file in mask_files:
            mask = Image.open(mask_file).convert("L").resize((image_size, image_size), Image.NEAREST)
            merged_mask |= np.asarray(mask, dtype=np.uint8) > 0

        images.append(image_array[np.newaxis, ...])
        masks.append(merged_mask.astype(np.float32)[np.newaxis, ...])
        case_ids.append(case_dir.name)

    if not images:
        raise FileNotFoundError("BBBC038 cases were found, but no usable image-mask pairs were loaded.")

    source = describe_source("bbbc038_nuclei")
    metadata = {
        "source": source,
        "source_url": source_url,
        "archive_path": str(archive_path),
        "image_size": int(image_size),
        "selected_case_ids": case_ids,
        "selected_positions": selected_positions.astype(int).tolist(),
        "mask_policy": "Per-nucleus PNG masks merged into one binary foreground mask.",
    }
    return (
        np.stack(images).astype(np.float32),
        np.stack(masks).astype(np.float32),
        metadata,
    )
