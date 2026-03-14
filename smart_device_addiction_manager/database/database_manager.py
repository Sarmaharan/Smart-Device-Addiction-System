"""SQLite persistence for the application."""

from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Generator, List, Optional, Tuple


class DatabaseManager:
    """Thread-safe SQLite access layer."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        base_path = Path(__file__).resolve().parents[2]
        self.db_path = str(base_path / "addiction_manager.db") if db_path is None else db_path
        self._lock = threading.Lock()
        self._initialize_database()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        connection = sqlite3.connect(self.db_path, timeout=15, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize_database(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    duration REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS app_limits (
                    app_name TEXT PRIMARY KEY,
                    daily_limit INTEGER NOT NULL
                )
                """
            )

    def insert_usage_log(self, app_name: str, start_time: str, end_time: str, duration: float) -> None:
        with self._lock, self._get_connection() as conn:
            conn.execute(
                "INSERT INTO usage_logs (app_name, start_time, end_time, duration) VALUES (?, ?, ?, ?)",
                (app_name, start_time, end_time, duration),
            )

    def fetch_usage_by_date(self, usage_date: date) -> List[sqlite3.Row]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM usage_logs
                WHERE DATE(start_time) = ?
                ORDER BY start_time ASC
                """,
                (usage_date.isoformat(),),
            )
            return cursor.fetchall()

    def fetch_usage_by_month(self, year: int, month: int) -> List[sqlite3.Row]:
        pattern = f"{year:04d}-{month:02d}-%"
        with self._lock, self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM usage_logs
                WHERE start_time LIKE ?
                ORDER BY start_time ASC
                """,
                (pattern,),
            )
            return cursor.fetchall()

    def fetch_daily_totals(self, days: int = 30) -> List[Tuple[str, float]]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT DATE(start_time) AS day, SUM(duration) AS total_duration
                FROM usage_logs
                GROUP BY DATE(start_time)
                ORDER BY day DESC
                LIMIT ?
                """,
                (days,),
            )
            return [(row["day"], float(row["total_duration"] or 0.0)) for row in cursor.fetchall()]

    def upsert_app_limit(self, app_name: str, daily_limit: int) -> None:
        with self._lock, self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO app_limits (app_name, daily_limit)
                VALUES (?, ?)
                ON CONFLICT(app_name)
                DO UPDATE SET daily_limit = excluded.daily_limit
                """,
                (app_name, daily_limit),
            )

    def fetch_app_limits(self) -> List[sqlite3.Row]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.execute("SELECT app_name, daily_limit FROM app_limits ORDER BY app_name")
            return cursor.fetchall()

    def delete_app_limit(self, app_name: str) -> None:
        with self._lock, self._get_connection() as conn:
            conn.execute("DELETE FROM app_limits WHERE app_name = ?", (app_name,))
