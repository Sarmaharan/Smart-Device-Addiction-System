"""Reports and visualization page."""

from __future__ import annotations

from datetime import date

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

from smart_device_addiction_manager.gui.theme import HEADER_FONT, PADDING, THEME
from smart_device_addiction_manager.utils.helpers import parse_date, parse_month


class ReportsPage(ctk.CTkFrame):
    def __init__(self, master, database, productivity_service, **kwargs):
        super().__init__(master, fg_color=THEME.bg, **kwargs)
        self.database = database
        self.productivity_service = productivity_service
        self.canvas = None

        ctk.CTkLabel(self, text="Reports & Visualization", font=HEADER_FONT, text_color=THEME.text).pack(
            anchor="w", padx=PADDING, pady=PADDING
        )

        filters = ctk.CTkFrame(self, fg_color=THEME.panel, border_color=THEME.border, border_width=1)
        filters.pack(fill="x", padx=PADDING)

        self.date_entry = ctk.CTkEntry(
            filters,
            placeholder_text="Date (YYYY-MM-DD)",
            fg_color=THEME.panel_2,
            border_color=THEME.border,
            text_color=THEME.text,
        )
        self.date_entry.pack(side="left", padx=5, pady=8)
        self.month_entry = ctk.CTkEntry(
            filters,
            placeholder_text="Month (YYYY-MM)",
            fg_color=THEME.panel_2,
            border_color=THEME.border,
            text_color=THEME.text,
        )
        self.month_entry.pack(side="left", padx=5, pady=8)

        ctk.CTkButton(filters, text="Load Date", command=self.load_by_date, fg_color=THEME.accent, hover_color=THEME.accent_2).pack(
            side="left", padx=5
        )
        ctk.CTkButton(filters, text="Load Month", command=self.load_by_month, fg_color=THEME.accent, hover_color=THEME.accent_2).pack(
            side="left", padx=5
        )

        self.chart_frame = ctk.CTkFrame(self, fg_color=THEME.panel, border_color=THEME.border, border_width=1)
        self.chart_frame.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)

        self.date_entry.insert(0, date.today().isoformat())
        self.load_by_date()

    def _render_figure(self, figure):
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(figure, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _new_figure(self):
        figure, axes = plt.subplots(1, 2, figsize=(10, 4))
        figure.patch.set_facecolor(THEME.panel)
        for ax in axes:
            ax.set_facecolor(THEME.panel_2)
            ax.tick_params(colors=THEME.muted)
            for spine in ax.spines.values():
                spine.set_color(THEME.border)
            ax.title.set_color(THEME.text)
        figure.tight_layout(pad=2)
        return figure, axes

    def load_by_date(self):
        try:
            selected_date = parse_date(self.date_entry.get().strip())
        except ValueError:
            return

        rows = self.database.fetch_usage_by_date(selected_date)
        frame = pd.DataFrame([dict(r) for r in rows])

        figure, axes = self._new_figure()

        if frame.empty:
            axes[0].text(0.5, 0.5, "No Data", ha="center", color=THEME.text)
            axes[1].text(0.5, 0.5, "No Data", ha="center", color=THEME.text)
        else:
            per_app = frame.groupby("app_name")["duration"].sum().sort_values(ascending=False)
            axes[0].bar(per_app.index, per_app.values, color=THEME.accent_2)
            axes[0].set_title("Application Usage Distribution")
            axes[0].tick_params(axis="x", rotation=45)

            axes[1].pie(per_app.values, labels=per_app.index, autopct="%1.1f%%")
            axes[1].set_title("Daily Screen Time Split")

        self._render_figure(figure)

    def load_by_month(self):
        try:
            year, month = parse_month(self.month_entry.get().strip())
        except ValueError:
            return

        rows = self.database.fetch_usage_by_month(year, month)
        frame = pd.DataFrame([dict(r) for r in rows])

        figure, axes = self._new_figure()

        if frame.empty:
            axes[0].text(0.5, 0.5, "No Data", ha="center", color=THEME.text)
            axes[1].text(0.5, 0.5, "No Data", ha="center", color=THEME.text)
        else:
            frame["day"] = pd.to_datetime(frame["start_time"]).dt.date.astype(str)
            daily = frame.groupby("day")["duration"].sum()
            axes[0].plot(daily.index, daily.values, marker="o", color=THEME.accent_2)
            axes[0].set_title("Weekly/Daily Usage Trend")
            axes[0].tick_params(axis="x", rotation=45)

            productivity = self.productivity_service.productivity_trend(days=30)
            axes[1].plot(list(productivity.keys()), list(productivity.values()), color=THEME.good, marker="x")
            axes[1].set_title("Productivity Trend")
            axes[1].tick_params(axis="x", rotation=45)

        self._render_figure(figure)
