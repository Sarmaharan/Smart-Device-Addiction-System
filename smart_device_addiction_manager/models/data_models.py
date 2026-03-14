"""Data models used by the system."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class UsageEntry:
    app_name: str
    start_time: str
    end_time: str
    duration: float


@dataclass(slots=True)
class AppLimit:
    app_name: str
    daily_limit: int


@dataclass(slots=True)
class AnalyticsSnapshot:
    total_screen_time: float
    productivity_score: float
    addiction_risk_score: float
    addiction_level: str
