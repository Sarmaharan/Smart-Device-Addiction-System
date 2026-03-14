"""Main dashboard application window."""

from __future__ import annotations

from datetime import date
from tkinter import messagebox

import customtkinter as ctk

from smart_device_addiction_manager.database.database_manager import DatabaseManager
from smart_device_addiction_manager.gui.components import BlinkingIndicator
from smart_device_addiction_manager.gui.limits_page import LimitsPage
from smart_device_addiction_manager.gui.reports_page import ReportsPage
from smart_device_addiction_manager.gui.settings_page import SettingsPage
from smart_device_addiction_manager.gui.theme import HEADER_FONT, NORMAL_FONT, TITLE_FONT, PADDING
from smart_device_addiction_manager.gui.usage_page import UsagePage
from smart_device_addiction_manager.services.alert_service import AlertService
from smart_device_addiction_manager.services.prediction_service import PredictionService
from smart_device_addiction_manager.services.productivity_service import ProductivityService
from smart_device_addiction_manager.services.risk_analyzer import RiskAnalyzer
from smart_device_addiction_manager.services.usage_monitor import UsageMonitor
from smart_device_addiction_manager.utils.helpers import format_seconds


class SmartDeviceAddictionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SMART DEVICE ADDICTION MANAGER")
        self.geometry("1200x760")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.database = DatabaseManager()
        self.productivity_service = ProductivityService(self.database)
        self.alert_service = AlertService(self.database)
        self.prediction_service = PredictionService(self.database)
        self.risk_analyzer = RiskAnalyzer(self.productivity_service)
        self.monitor = UsageMonitor(
            self.database,
            self.productivity_service,
            self.alert_service,
            on_violation=self._handle_violation,
        )

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._build_layout()
        self.monitor.start()
        self.refresh_dashboard()

    def _build_layout(self):
        ctk.CTkLabel(self, text="SMART DEVICE ADDICTION MANAGER", font=TITLE_FONT).pack(anchor="w", padx=PADDING, pady=PADDING)

        self.indicator = BlinkingIndicator(self)
        self.indicator.pack(anchor="w", padx=PADDING)
        self.indicator.start()

        container = ctk.CTkTabview(self)
        container.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)

        dashboard_tab = container.add("Dashboard")
        usage_tab = container.add("Usage")
        limits_tab = container.add("Limits")
        reports_tab = container.add("Reports")
        settings_tab = container.add("Settings")

        self._build_dashboard_tab(dashboard_tab)
        self.usage_page = UsagePage(usage_tab, self.productivity_service)
        self.usage_page.pack(fill="both", expand=True)
        self.limits_page = LimitsPage(limits_tab, self.database)
        self.limits_page.pack(fill="both", expand=True)
        self.reports_page = ReportsPage(reports_tab, self.database, self.productivity_service)
        self.reports_page.pack(fill="both", expand=True)
        self.settings_page = SettingsPage(settings_tab, self.monitor)
        self.settings_page.pack(fill="both", expand=True)

    def _build_dashboard_tab(self, parent):
        cards = ctk.CTkFrame(parent)
        cards.pack(fill="x", padx=PADDING, pady=PADDING)

        self.total_time_label = ctk.CTkLabel(cards, text="Total Screen Time Today: 00:00:00", font=HEADER_FONT)
        self.total_time_label.pack(anchor="w", padx=10, pady=6)

        self.productivity_label = ctk.CTkLabel(cards, text="Productivity Score: 0%", font=NORMAL_FONT)
        self.productivity_label.pack(anchor="w", padx=10, pady=6)

        self.risk_label = ctk.CTkLabel(cards, text="Addiction Risk Level: Low", font=NORMAL_FONT)
        self.risk_label.pack(anchor="w", padx=10, pady=6)

        self.prediction_label = ctk.CTkLabel(cards, text="Predicted Next Day Usage: N/A", font=NORMAL_FONT)
        self.prediction_label.pack(anchor="w", padx=10, pady=6)

        self.top_apps = ctk.CTkTextbox(parent, height=320, font=NORMAL_FONT)
        self.top_apps.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)

        ctk.CTkButton(parent, text="Refresh Dashboard", command=self.refresh_dashboard).pack(anchor="e", padx=PADDING)

    def refresh_dashboard(self):
        summary = self.productivity_service.get_daily_summary(date.today())
        risk = self.risk_analyzer.analyze(date.today())
        top_apps = self.productivity_service.get_top_apps(date.today())
        prediction = self.prediction_service.prediction_summary()

        self.total_time_label.configure(text=f"Total Screen Time Today: {format_seconds(summary['total_screen_time'])}")
        self.productivity_label.configure(text=f"Productivity Score: {summary['productivity_score']:.2f}%")
        self.risk_label.configure(text=f"Addiction Risk Level: {risk['risk_level']} ({risk['risk_score']:.2f})")
        self.prediction_label.configure(text=f"Predicted Next Day Usage: {prediction['value']}")

        lines = ["Top Used Applications:"]
        if not top_apps:
            lines.append("- No data yet")
        else:
            for app_name, duration in top_apps:
                lines.append(f"- {app_name}: {format_seconds(duration)}")

        self.top_apps.delete("1.0", "end")
        self.top_apps.insert("end", "\n".join(lines))

    def _handle_violation(self, app_name: str, terminated: bool) -> None:
        if terminated:
            message = f"Strict limit reached. {app_name} was terminated."
        else:
            message = f"Warning: {app_name} exceeded its daily limit."
        self.after(0, lambda: messagebox.showwarning("Usage Limit", message))

    def on_close(self):
        self.monitor.stop()
        self.destroy()
