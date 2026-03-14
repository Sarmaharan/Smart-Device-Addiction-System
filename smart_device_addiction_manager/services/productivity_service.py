"""Productivity and usage analytics service."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Dict, Iterable, List, Tuple

import pandas as pd

from smart_device_addiction_manager.database.database_manager import DatabaseManager


class ProductivityService:
    """Aggregates usage logs into actionable analytics."""

    PRODUCTIVE_KEYWORDS = ("code", "pycharm", "vscode", "word", "excel", "terminal", "notepad")

    def __init__(self, database: DatabaseManager) -> None:
        self.database = database

    def _to_dataframe(self, rows: Iterable) -> pd.DataFrame:
        records = [dict(row) for row in rows]
        if not records:
            return pd.DataFrame(columns=["app_name", "start_time", "duration"])
        return pd.DataFrame(records)

    def get_daily_summary(self, usage_date: date) -> Dict[str, float]:
        df = self._to_dataframe(self.database.fetch_usage_by_date(usage_date))
        total = float(df["duration"].sum()) if not df.empty else 0.0
        return {
            "total_screen_time": total,
            "productivity_score": self.calculate_productivity_score(df),
        }

    def get_time_per_app(self, usage_date: date) -> Dict[str, float]:
        df = self._to_dataframe(self.database.fetch_usage_by_date(usage_date))
        if df.empty:
            return {}
        grouped = df.groupby("app_name")["duration"].sum().sort_values(ascending=False)
        return grouped.to_dict()

    def get_top_apps(self, usage_date: date, top_n: int = 5) -> List[Tuple[str, float]]:
        data = self.get_time_per_app(usage_date)
        return list(data.items())[:top_n]

    def calculate_productivity_score(self, df: pd.DataFrame) -> float:
        if df.empty:
            return 100.0

        productive_time = 0.0
        total_time = float(df["duration"].sum())
        for _, row in df.iterrows():
            app_name = str(row["app_name"]).lower()
            if any(keyword in app_name for keyword in self.PRODUCTIVE_KEYWORDS):
                productive_time += float(row["duration"])

        score = (productive_time / total_time) * 100 if total_time > 0 else 0
        return round(max(0.0, min(score, 100.0)), 2)

    def get_weekly_usage_trend(self, days: int = 7) -> Dict[str, float]:
        daily_totals = self.database.fetch_daily_totals(days=days)
        return dict(reversed(daily_totals))

    def productivity_trend(self, days: int = 7) -> Dict[str, float]:
        trend: Dict[str, float] = defaultdict(float)
        daily_totals = self.database.fetch_daily_totals(days=days)
        for day, _ in daily_totals:
            day_df = self._to_dataframe(self.database.fetch_usage_by_date(date.fromisoformat(day)))
            trend[day] = self.calculate_productivity_score(day_df)
        return dict(reversed(trend.items()))
