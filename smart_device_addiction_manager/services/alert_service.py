"""Usage-limit alert and enforcement service."""

from __future__ import annotations

from datetime import date
from typing import Dict, Set

from smart_device_addiction_manager.database.database_manager import DatabaseManager


class AlertService:
    """Evaluates app limit violations and handles one-time actions."""

    def __init__(self, database: DatabaseManager) -> None:
        self.database = database
        self._violations_alerted: Set[str] = set()
        self._violations_terminated: Set[str] = set()
        self._last_reset_day = date.today()

    def reset_daily_state_if_needed(self) -> None:
        today = date.today()
        if today != self._last_reset_day:
            self._violations_alerted.clear()
            self._violations_terminated.clear()
            self._last_reset_day = today

    def check_limits(self, usage_by_app: Dict[str, float], strict_mode: bool = False) -> Dict[str, Dict[str, bool]]:
        self.reset_daily_state_if_needed()
        limits = {row["app_name"]: int(row["daily_limit"]) for row in self.database.fetch_app_limits()}
        results: Dict[str, Dict[str, bool]] = {}

        for app_name, used_seconds in usage_by_app.items():
            limit_minutes = limits.get(app_name)
            if limit_minutes is None:
                continue

            exceeded = used_seconds > (limit_minutes * 60)
            if not exceeded:
                continue

            alert_now = app_name not in self._violations_alerted
            terminate_now = strict_mode and app_name not in self._violations_terminated

            if alert_now:
                self._violations_alerted.add(app_name)
            if terminate_now:
                self._violations_terminated.add(app_name)

            results[app_name] = {
                "alert": alert_now,
                "terminate": terminate_now,
            }
        return results
