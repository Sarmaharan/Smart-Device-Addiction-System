"""Usage analytics page."""

from __future__ import annotations

from datetime import date

import customtkinter as ctk

from smart_device_addiction_manager.gui.theme import HEADER_FONT, NORMAL_FONT, PADDING, THEME
from smart_device_addiction_manager.utils.helpers import format_seconds


class UsagePage(ctk.CTkFrame):
    def __init__(self, master, productivity_service, **kwargs):
        super().__init__(master, fg_color=THEME.bg, **kwargs)
        self.productivity_service = productivity_service

        ctk.CTkLabel(self, text="Screen Time Analytics", font=HEADER_FONT, text_color=THEME.text).pack(
            anchor="w", padx=PADDING, pady=PADDING
        )
        self.output = ctk.CTkTextbox(
            self,
            height=380,
            font=NORMAL_FONT,
            fg_color=THEME.panel,
            border_color=THEME.border,
            border_width=1,
            text_color=THEME.text,
        )
        self.output.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)

        refresh_btn = ctk.CTkButton(
            self,
            text="Refresh",
            command=self.refresh,
            fg_color=THEME.accent,
            hover_color=THEME.accent_2,
            text_color=THEME.text,
        )
        refresh_btn.pack(anchor="e", padx=PADDING, pady=(0, PADDING))
        self.refresh()

    def refresh(self) -> None:
        usage_date = date.today()
        summary = self.productivity_service.get_daily_summary(usage_date)
        time_per_app = self.productivity_service.get_time_per_app(usage_date)

        lines = [
            f"Date: {usage_date.isoformat()}",
            f"Total Screen Time: {format_seconds(summary['total_screen_time'])}",
            f"Productivity Score: {summary['productivity_score']:.2f}%",
            "",
            "Time per Application:",
        ]

        if not time_per_app:
            lines.append("- No data available yet.")
        else:
            for app_name, duration in time_per_app.items():
                lines.append(f"- {app_name}: {format_seconds(duration)}")

        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines))
