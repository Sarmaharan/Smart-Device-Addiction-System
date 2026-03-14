"""App limits management page."""

from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from smart_device_addiction_manager.gui.theme import HEADER_FONT, PADDING


class LimitsPage(ctk.CTkFrame):
    def __init__(self, master, database, **kwargs):
        super().__init__(master, **kwargs)
        self.database = database

        ctk.CTkLabel(self, text="Usage Limits", font=HEADER_FONT).pack(anchor="w", padx=PADDING, pady=PADDING)

        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=PADDING)

        self.app_name = ctk.CTkEntry(form, placeholder_text="Application executable (e.g., chrome.exe)")
        self.app_name.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)

        self.limit_minutes = ctk.CTkEntry(form, placeholder_text="Daily limit in minutes")
        self.limit_minutes.pack(side="left", fill="x", expand=True, padx=5, pady=10)

        ctk.CTkButton(form, text="Save", command=self.save_limit).pack(side="left", padx=(5, 10), pady=10)

        self.list_box = ctk.CTkTextbox(self, height=360)
        self.list_box.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)

        ctk.CTkButton(self, text="Delete Selected App", command=self.delete_limit).pack(anchor="e", padx=PADDING)
        self.refresh()

    def save_limit(self) -> None:
        app = self.app_name.get().strip()
        limit_text = self.limit_minutes.get().strip()

        if not app:
            messagebox.showwarning("Validation", "Application name cannot be empty.")
            return
        if not limit_text.isdigit() or int(limit_text) <= 0:
            messagebox.showwarning("Validation", "Daily limit must be a positive integer.")
            return

        self.database.upsert_app_limit(app, int(limit_text))
        self.refresh()

    def refresh(self) -> None:
        limits = self.database.fetch_app_limits()
        lines = ["Configured limits:"]
        for row in limits:
            lines.append(f"- {row['app_name']}: {row['daily_limit']} minutes")

        self.list_box.delete("1.0", "end")
        self.list_box.insert("end", "\n".join(lines))

    def delete_limit(self) -> None:
        app = self.app_name.get().strip()
        if not app:
            messagebox.showwarning("Validation", "Enter an application name to delete.")
            return
        self.database.delete_app_limit(app)
        self.refresh()
