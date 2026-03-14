"""Theme constants and fonts for UI consistency."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    bg: str = "#0b1020"
    panel: str = "#111a33"
    panel_2: str = "#0f1730"
    text: str = "#e7ecff"
    muted: str = "#a9b3d6"
    border: str = "#263258"
    accent: str = "#6c5ce7"  # purple-blue
    accent_2: str = "#2d9cdb"  # blue
    good: str = "#2ecc71"
    warn: str = "#f2c94c"
    bad: str = "#eb5757"


THEME = Theme()

TITLE_FONT = ("Segoe UI", 22, "bold")
HEADER_FONT = ("Segoe UI", 17, "bold")
NORMAL_FONT = ("Segoe UI", 13)
SMALL_FONT = ("Segoe UI", 11)

PADDING = 12
