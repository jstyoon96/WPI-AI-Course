"""Matplotlib helpers for WPI-branded notebook figures."""

from __future__ import annotations

from .colors import WPI_COLORS, WPI_COLOR_CYCLE


def wpi_color_cycle() -> tuple[str, ...]:
    """Return the default color cycle for course plots."""

    return WPI_COLOR_CYCLE


def apply_wpi_plot_style() -> None:
    """Apply WPI AI Bootcamp matplotlib defaults.

    The import happens inside the function so static repository checks do not
    require matplotlib to be installed.
    """

    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        return

    style = {
        "axes.edgecolor": WPI_COLORS["dark_gray"],
        "axes.facecolor": WPI_COLORS["white"],
        "axes.grid": True,
        "axes.labelcolor": WPI_COLORS["dark_gray"],
        "axes.spines.right": False,
        "axes.spines.top": False,
        "figure.facecolor": WPI_COLORS["white"],
        "figure.dpi": 120,
        "font.size": 11,
        "grid.color": WPI_COLORS["grid_gray"],
        "grid.linewidth": 0.8,
        "legend.frameon": False,
        "savefig.bbox": "tight",
        "savefig.dpi": 180,
        "text.color": WPI_COLORS["dark_gray"],
        "xtick.color": WPI_COLORS["dark_gray"],
        "ytick.color": WPI_COLORS["dark_gray"],
    }
    try:
        from cycler import cycler
    except ModuleNotFoundError:
        pass
    else:
        style["axes.prop_cycle"] = cycler(color=WPI_COLOR_CYCLE)

    plt.rcParams.update(style)
