"""Settings page with validation."""

from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from smart_device_addiction_manager.gui.theme import HEADER_FONT, NORMAL_FONT, PADDING


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, monitor, **kwargs):
        super().__init__(master, **kwargs)
        self.monitor = monitor

        ctk.CTkLabel(self, text="Settings", font=HEADER_FONT).pack(anchor="w", padx=PADDING, pady=PADDING)

        monitor_section = ctk.CTkFrame(self)
        monitor_section.pack(fill="x", padx=PADDING, pady=6)
        ctk.CTkLabel(monitor_section, text="Monitoring Settings", font=NORMAL_FONT).pack(anchor="w", padx=10, pady=(8, 0))

        self.interval_entry = ctk.CTkEntry(monitor_section, placeholder_text="Polling interval seconds (>=5)")
        self.interval_entry.insert(0, str(self.monitor.POLL_INTERVAL_SECONDS))
        self.interval_entry.pack(fill="x", padx=10, pady=10)

        alert_section = ctk.CTkFrame(self)
        alert_section.pack(fill="x", padx=PADDING, pady=6)
        ctk.CTkLabel(alert_section, text="Alert Settings", font=NORMAL_FONT).pack(anchor="w", padx=10, pady=(8, 0))

        self.strict_switch = ctk.CTkSwitch(alert_section, text="Enable strict limits (terminate once)")
        self.strict_switch.pack(anchor="w", padx=10, pady=10)

        data_section = ctk.CTkFrame(self)
        data_section.pack(fill="x", padx=PADDING, pady=6)
        ctk.CTkLabel(data_section, text="Data Settings", font=NORMAL_FONT).pack(anchor="w", padx=10, pady=(8, 0))
        ctk.CTkLabel(data_section, text="Data stored locally in SQLite database.").pack(anchor="w", padx=10, pady=(4, 10))

        ctk.CTkButton(self, text="Save Settings", command=self.save).pack(anchor="e", padx=PADDING, pady=PADDING)

    def save(self) -> None:
        interval_text = self.interval_entry.get().strip()
        if not interval_text.isdigit() or int(interval_text) < 5:
            messagebox.showwarning("Validation", "Polling interval must be an integer >= 5.")
            return

        self.monitor.POLL_INTERVAL_SECONDS = int(interval_text)
        self.monitor.set_strict_mode(self.strict_switch.get() == 1)
        messagebox.showinfo("Settings", "Settings saved successfully.")
