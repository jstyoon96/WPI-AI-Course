"""Color tokens for WPI AI Bootcamp visuals."""

from __future__ import annotations

WPI_SOURCE = (
    "WPI Institutional Guidelines: official colors are Crimson PMS 187c "
    "(HTML #AC2B37), Gray PMS 429c (HTML #A9B0B7), and Black #000000."
)

WPI_COLORS: dict[str, str] = {
    "crimson": "#AC2B37",
    "gray": "#A9B0B7",
    "black": "#000000",
    "white": "#FFFFFF",
    "dark_gray": "#2E2E2E",
    "light_gray": "#EEF0F2",
    "grid_gray": "#D8DDE1",
    "accent_blue": "#2364AA",
    "accent_green": "#2E7D32",
    "accent_gold": "#B58500",
}

WPI_COLOR_CYCLE: tuple[str, ...] = (
    WPI_COLORS["crimson"],
    WPI_COLORS["black"],
    WPI_COLORS["gray"],
    WPI_COLORS["accent_blue"],
    WPI_COLORS["accent_green"],
    WPI_COLORS["accent_gold"],
)
