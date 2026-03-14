"""Addiction risk analysis service."""

from __future__ import annotations

from datetime import date
from typing import Dict

from smart_device_addiction_manager.services.productivity_service import ProductivityService


class RiskAnalyzer:
    """Computes addiction risk scores from usage behavior."""

    def __init__(self, productivity_service: ProductivityService) -> None:
        self.productivity_service = productivity_service

    def analyze(self, usage_date: date) -> Dict[str, float | str | bool]:
        summary = self.productivity_service.get_daily_summary(usage_date)
        total_hours = summary["total_screen_time"] / 3600
        productivity = summary["productivity_score"]

        excessive_usage = total_hours >= 8
        risk_score = min(100.0, (total_hours * 8) + (100 - productivity) * 0.4)

        if risk_score < 35:
            level = "Low"
        elif risk_score < 70:
            level = "Moderate"
        else:
            level = "High"

        return {
            "excessive_usage": excessive_usage,
            "risk_score": round(risk_score, 2),
            "risk_level": level,
        }
