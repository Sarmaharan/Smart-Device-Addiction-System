"""Screen-time prediction service using linear regression."""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np
from sklearn.linear_model import LinearRegression

from smart_device_addiction_manager.database.database_manager import DatabaseManager


class PredictionService:
    """Predicts next-day expected screen time."""

    def __init__(self, database: DatabaseManager) -> None:
        self.database = database

    def predict_next_day_seconds(self) -> Optional[float]:
        data = list(reversed(self.database.fetch_daily_totals(days=45)))
        if len(data) < 2:
            return None

        y = np.array([duration for _, duration in data], dtype=float)
        x = np.arange(len(y)).reshape(-1, 1)
        model = LinearRegression()
        model.fit(x, y)
        prediction = float(model.predict(np.array([[len(y)]]))[0])
        return max(0.0, prediction)

    def prediction_summary(self) -> Dict[str, str]:
        predicted_seconds = self.predict_next_day_seconds()
        if predicted_seconds is None:
            return {"status": "Insufficient historical data", "value": "N/A"}

        hours = predicted_seconds / 3600
        return {"status": "Prediction ready", "value": f"{hours:.2f} hours"}
