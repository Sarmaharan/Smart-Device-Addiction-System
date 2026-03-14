"""Reusable GUI widgets."""

from __future__ import annotations

import customtkinter as ctk


class BlinkingIndicator(ctk.CTkFrame):
    """Simple blinking indicator for monitor status."""

    def __init__(self, master, text: str = "Monitoring Active", **kwargs):
        super().__init__(master, **kwargs)
        self._visible = True
        self.dot = ctk.CTkLabel(self, text="●", text_color="green", font=("Segoe UI", 20, "bold"))
        self.dot.pack(side="left", padx=(0, 5))
        self.label = ctk.CTkLabel(self, text=text)
        self.label.pack(side="left")

    def start(self) -> None:
        self._blink()

    def _blink(self) -> None:
        self._visible = not self._visible
        self.dot.configure(text_color="green" if self._visible else "gray")
        self.after(700, self._blink)
