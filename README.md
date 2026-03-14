# SMART DEVICE ADDICTION MANAGER

Smart Device Addiction Manager is a modular Python desktop application designed to monitor and control computer usage behavior in real time. It tracks foreground application usage, generates analytics, predicts next-day usage with machine learning, enforces app limits, and provides charts and reports.

## Features

- App usage tracking (foreground app detection every 10 seconds)
- Screen time analytics (daily total, per-app usage, top apps)
- Addiction risk analysis (risk score + level classification)
- AI usage prediction (Linear Regression for next-day screen time)
- Usage limits and alerts (with optional strict one-time termination)
- Date and month based reports with visual charts
- Background monitoring status indicator (blinking activity light)
- Dedicated settings page with grouped configuration and input validation

## Architecture

The project uses a clean modular structure:

- `database/`: SQLite manager and schema creation
- `services/`: monitoring, analytics, prediction, risk, alerts
- `models/`: dataclasses for domain entities
- `utils/`: helper functions (formatting/parsing)
- `gui/`: CustomTkinter pages/components/theme

## Database

SQLite database file: `addiction_manager.db`

Tables:

1. `usage_logs`
   - `id`
   - `app_name`
   - `start_time`
   - `end_time`
   - `duration`

2. `app_limits`
   - `app_name`
   - `daily_limit`

## Run Instructions

```bash
pip install -r requirements.txt
python main.py
```

## Notes

- The app is designed for Windows foreground-process detection using `ctypes`.
- On non-Windows systems, a safe fallback app name is used for development/testing.
- Background monitoring runs in a separate daemon thread to keep the GUI responsive.
