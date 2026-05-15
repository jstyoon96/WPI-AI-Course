"""Student-facing notebook helpers for WPI AI Course labs."""

from __future__ import annotations

from .style import WPI_COLORS, apply_wpi_plot_style


def setup_lab() -> dict[str, str]:
    """Apply the course plot style and return shared color tokens."""

    apply_wpi_plot_style()
    return WPI_COLORS


def make_wpi_overlay(gray01, binary_mask, alpha: float = 0.45):
    """Overlay a binary mask on a grayscale image using WPI Crimson."""

    import numpy as np

    base = np.dstack([gray01, gray01, gray01])
    crimson = np.array([172, 43, 55], dtype=np.float32) / 255.0
    overlay = base.copy()
    overlay[binary_mask] = (1 - alpha) * base[binary_mask] + alpha * crimson
    return np.clip(overlay, 0, 1)
