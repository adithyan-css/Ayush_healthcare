from app.services.ml_service import MLService


class WearableService:
    def __init__(self):
        self._ml = MLService()

    def detect_nadi(self, hrv_ms: float) -> str:
        return self._ml.detect_nadi_type(hrv_ms)

    def is_anomaly(self, readings: list[float]) -> bool:
        return self._ml.detect_anomaly(readings)

    def build_nadi_summary(self, readings: list[float], anomaly_flags: list[bool]) -> dict:
        if not readings:
            return {'type': 'Unknown', 'hrv_ms': 0.0, 'stress_index': 0.0, 'is_anomaly': False}
        avg = sum(readings) / len(readings)
        return {
            'type': self.detect_nadi(avg),
            'hrv_ms': round(avg, 2),
            'stress_index': round(500 / avg if avg > 0 else 100, 2),
            'is_anomaly': any(anomaly_flags),
        }
