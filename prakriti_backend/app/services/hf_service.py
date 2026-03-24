from __future__ import annotations

import importlib
from threading import Lock
from typing import Any


class HFService:
    _pipeline = None
    _load_error: str | None = None
    _lock = Lock()

    def __init__(self) -> None:
        self.model_name = 'distilbert-base-uncased'

    @classmethod
    def _ensure_loaded(cls) -> None:
        if cls._pipeline is not None or cls._load_error is not None:
            return
        with cls._lock:
            if cls._pipeline is not None or cls._load_error is not None:
                return
            try:
                transformers_module = importlib.import_module('transformers')
                pipeline = getattr(transformers_module, 'pipeline')
                cls._pipeline = pipeline('feature-extraction', model='distilbert-base-uncased')
            except Exception as exc:
                cls._load_error = str(exc)

    def classify_symptoms(self, text: str) -> dict[str, Any]:
        self._ensure_loaded()
        symptom_text = (text or '').strip().lower()
        if not symptom_text:
            return {
                'dosha': 'vata',
                'confidence': 0.5,
                'scores': {'vata': 1.0, 'pitta': 1.0, 'kapha': 1.0},
                'model': self.model_name,
                'model_loaded': self._pipeline is not None,
            }

        dosha_keywords = {
            'vata': ['anxiety', 'dryness', 'constipation', 'insomnia', 'bloating', 'gas', 'worry'],
            'pitta': ['acidity', 'anger', 'heat', 'burning', 'inflammation', 'rash', 'irritability'],
            'kapha': ['lethargy', 'weight gain', 'sluggish', 'mucus', 'congestion', 'heaviness'],
        }

        scores: dict[str, float] = {'vata': 0.0, 'pitta': 0.0, 'kapha': 0.0}
        for dosha, words in dosha_keywords.items():
            for word in words:
                if word in symptom_text:
                    scores[dosha] += 1.0

        if self._pipeline is not None:
            try:
                vectors = self._pipeline(symptom_text[:256], truncation=True)
                if isinstance(vectors, list) and vectors:
                    first = vectors[0]
                    if isinstance(first, list) and first:
                        avg_signal = sum(abs(float(v)) for v in first[0][:8]) / max(1, len(first[0][:8]))
                        if 'heat' in symptom_text or 'acidity' in symptom_text:
                            scores['pitta'] += avg_signal
                        elif 'mucus' in symptom_text or 'weight' in symptom_text:
                            scores['kapha'] += avg_signal
                        else:
                            scores['vata'] += avg_signal
            except Exception:
                pass

        if max(scores.values()) == 0:
            scores['vata'] = 1.0

        top_dosha = max(scores.items(), key=lambda item: item[1])[0]
        total = sum(scores.values()) or 1.0
        confidence = round(float(scores[top_dosha] / total), 4)
        return {
            'dosha': top_dosha,
            'confidence': confidence,
            'scores': {k: round(v, 4) for k, v in scores.items()},
            'model': self.model_name,
            'model_loaded': self._pipeline is not None,
            'model_error': self._load_error,
        }
