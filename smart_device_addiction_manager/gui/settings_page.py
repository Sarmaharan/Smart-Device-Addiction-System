"""Settings page with validation."""

from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from smart_device_addiction_manager.gui.theme import HEADER_FONT, NORMAL_FONT, PADDING, THEME


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, monitor, **kwargs):
        super().__init__(master, fg_color=THEME.bg, **kwargs)
        self.monitor = monitor

        ctk.CTkLabel(self, text="Settings", font=HEADER_FONT, text_color=THEME.text).pack(anchor="w", padx=PADDING, pady=PADDING)

        monitor_section = ctk.CTkFrame(self, fg_color=THEME.panel, border_color=THEME.border, border_width=1)
        monitor_section.pack(fill="x", padx=PADDING, pady=6)
        ctk.CTkLabel(monitor_section, text="Monitoring Settings", font=NORMAL_FONT, text_color=THEME.text).pack(anchor="w", padx=10, pady=(8, 0))

        self.interval_entry = ctk.CTkEntry(
            monitor_section,
            placeholder_text="Polling interval seconds (>=5)",
            fg_color=THEME.panel_2,
            border_color=THEME.border,
            text_color=THEME.text,
        )
        self.interval_entry.insert(0, str(self.monitor.POLL_INTERVAL_SECONDS))
        self.interval_entry.pack(fill="x", padx=10, pady=10)

        alert_section = ctk.CTkFrame(self, fg_color=THEME.panel, border_color=THEME.border, border_width=1)
        alert_section.pack(fill="x", padx=PADDING, pady=6)
        ctk.CTkLabel(alert_section, text="Alert Settings", font=NORMAL_FONT, text_color=THEME.text).pack(anchor="w", padx=10, pady=(8, 0))

        self.strict_switch = ctk.CTkSwitch(
            alert_section,
            text="Enable strict limits (terminate once)",
            progress_color=THEME.accent,
            text_color=THEME.text,
        )
        self.strict_switch.pack(anchor="w", padx=10, pady=10)

        data_section = ctk.CTkFrame(self, fg_color=THEME.panel, border_color=THEME.border, border_width=1)
        data_section.pack(fill="x", padx=PADDING, pady=6)
        ctk.CTkLabel(data_section, text="Data Settings", font=NORMAL_FONT, text_color=THEME.text).pack(anchor="w", padx=10, pady=(8, 0))
        ctk.CTkLabel(data_section, text="Data stored locally in SQLite database.", text_color=THEME.muted).pack(anchor="w", padx=10, pady=(4, 10))

        ctk.CTkButton(
            self,
            text="Save Settings",
            command=self.save,
            fg_color=THEME.accent,
            hover_color=THEME.accent_2,
            text_color=THEME.text,
        ).pack(anchor="e", padx=PADDING, pady=PADDING)

    def save(self) -> None:
        interval_text = self.interval_entry.get().strip()
        if not interval_text.isdigit() or int(interval_text) < 5:
            messagebox.showwarning("Validation", "Polling interval must be an integer >= 5.")
            return

        self.monitor.POLL_INTERVAL_SECONDS = int(interval_text)
        self.monitor.set_strict_mode(self.strict_switch.get() == 1)
        messagebox.showinfo("Settings", "Settings saved successfully.")
