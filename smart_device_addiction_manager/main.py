"""Application bootstrap module."""

from smart_device_addiction_manager.gui.dashboard import SmartDeviceAddictionApp


def run() -> None:
    """Start the GUI application."""
    app = SmartDeviceAddictionApp()
    app.mainloop()
