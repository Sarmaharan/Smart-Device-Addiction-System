"""Reusable GUI widgets."""

from __future__ import annotations

import customtkinter as ctk

from smart_device_addiction_manager.gui.theme import THEME, NORMAL_FONT


class BlinkingIndicator(ctk.CTkFrame):
    """Simple blinking indicator for monitor status."""

    def __init__(self, master, text: str = "Monitoring Active", **kwargs):
        super().__init__(master, fg_color=THEME.panel_2, border_color=THEME.border, border_width=1, **kwargs)
        self._visible = True
        self.dot = ctk.CTkLabel(self, text="●", text_color=THEME.good, font=("Segoe UI", 20, "bold"))
        self.dot.pack(side="left", padx=(10, 5), pady=6)
        self.label = ctk.CTkLabel(self, text=text, text_color=THEME.text, font=NORMAL_FONT)
        self.label.pack(side="left", padx=(0, 10))

    def start(self) -> None:
        self._blink()

    def _blink(self) -> None:
        self._visible = not self._visible
        self.dot.configure(text_color=THEME.good if self._visible else THEME.muted)
        self.after(700, self._blink)
