"""Background usage monitor service."""

from __future__ import annotations

import ctypes
import ctypes.wintypes
import subprocess
import threading
import time
from datetime import datetime
from typing import Callable, Optional

from smart_device_addiction_manager.database.database_manager import DatabaseManager
from smart_device_addiction_manager.services.alert_service import AlertService
from smart_device_addiction_manager.services.productivity_service import ProductivityService


class UsageMonitor:
    """Tracks active foreground app every 10 seconds in a worker thread."""

    POLL_INTERVAL_SECONDS = 10

    def __init__(
        self,
        database: DatabaseManager,
        productivity_service: ProductivityService,
        alert_service: AlertService,
        on_violation: Optional[Callable[[str, bool], None]] = None,
    ) -> None:
        self.database = database
        self.productivity_service = productivity_service
        self.alert_service = alert_service
        self.on_violation = on_violation

        self.strict_limits_enabled = False
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._current_app: Optional[str] = None
        self._current_start: Optional[datetime] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self._finalize_current_session()

    def set_strict_mode(self, enabled: bool) -> None:
        self.strict_limits_enabled = enabled

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                active_app = self.get_foreground_application()
                self._track_switch(active_app)
                self._evaluate_limits()
            except Exception:
                # Keep monitor alive despite runtime issues.
                pass
            self._stop_event.wait(self.POLL_INTERVAL_SECONDS)

    def _track_switch(self, active_app: str) -> None:
        now = datetime.now()
        with self._lock:
            if self._current_app is None:
                self._current_app = active_app
                self._current_start = now
                return

            if active_app == self._current_app:
                return

            self._store_session(now)
            self._current_app = active_app
            self._current_start = now

    def _store_session(self, end_time: datetime) -> None:
        if self._current_app is None or self._current_start is None:
            return
        duration = max(0.0, (end_time - self._current_start).total_seconds())
        self.database.insert_usage_log(
            app_name=self._current_app,
            start_time=self._current_start.isoformat(sep=" ", timespec="seconds"),
            end_time=end_time.isoformat(sep=" ", timespec="seconds"),
            duration=duration,
        )

    def _finalize_current_session(self) -> None:
        with self._lock:
            if self._current_app and self._current_start:
                self._store_session(datetime.now())
                self._current_app = None
                self._current_start = None

    def _evaluate_limits(self) -> None:
        today_usage = self.productivity_service.get_time_per_app(datetime.now().date())
        violations = self.alert_service.check_limits(today_usage, strict_mode=self.strict_limits_enabled)
        for app_name, action in violations.items():
            if action["alert"] and self.on_violation:
                self.on_violation(app_name, False)
            if action["terminate"]:
                self._terminate_application(app_name)
                if self.on_violation:
                    self.on_violation(app_name, True)

    @staticmethod
    def _terminate_application(app_name: str) -> None:
        try:
            subprocess.run(
                ["taskkill", "/IM", app_name, "/F"],
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception:
            pass

    @staticmethod
    def get_foreground_application() -> str:
        if hasattr(ctypes, "windll"):
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            hwnd = user32.GetForegroundWindow()
            if hwnd == 0:
                return "Unknown"

            process_id = ctypes.wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))

            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            process_handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, process_id.value)
            if not process_handle:
                return "Unknown"

            try:
                buffer_length = ctypes.wintypes.DWORD(260)
                exe_name = ctypes.create_unicode_buffer(260)
                if kernel32.QueryFullProcessImageNameW(process_handle, 0, exe_name, ctypes.byref(buffer_length)):
                    return exe_name.value.split("\\")[-1]
                return "Unknown"
            finally:
                kernel32.CloseHandle(process_handle)

        # Non-Windows safe fallback for development/testing.
        return "UnsupportedPlatform"
