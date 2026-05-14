from wpi_ai_bootcamp.style import WPI_COLORS, WPI_COLOR_CYCLE, apply_wpi_plot_style


def test_wpi_color_tokens_match_brand_values():
    assert WPI_COLORS["crimson"] == "#AC2B37"
    assert WPI_COLORS["gray"] == "#A9B0B7"
    assert WPI_COLORS["black"] == "#000000"
    assert WPI_COLOR_CYCLE[0] == WPI_COLORS["crimson"]


def test_apply_wpi_plot_style_updates_matplotlib_defaults():
    import matplotlib.pyplot as plt

    apply_wpi_plot_style()

    assert plt.rcParams["axes.grid"] is True
    assert plt.rcParams["axes.edgecolor"] == WPI_COLORS["dark_gray"]
