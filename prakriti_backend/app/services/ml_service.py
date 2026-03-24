import math
import random


class MLService:
    def generate_forecast(self):
        days = list(range(30))
        conds = {'Respiratory': 30, 'Digestive': 20, 'Fever/Viral': 40, 'Skin': 15, 'Joint': 25}
        preds = {}
        for c, base in conds.items():
            preds[c] = [round(base + 10 * math.sin(d / 5) + random.uniform(-5, 5), 1) for d in days]
        cards = [
            {'region': 'Maharashtra', 'condition': 'Fever/Viral', 'peak_in_days': 5, 'severity': 'high'},
            {'region': 'Delhi', 'condition': 'Respiratory', 'peak_in_days': 12, 'severity': 'critical'},
            {'region': 'Karnataka', 'condition': 'Digestive', 'peak_in_days': 2, 'severity': 'medium'},
            {'region': 'Kerala', 'condition': 'Skin', 'peak_in_days': 28, 'severity': 'low'}
        ]
        pop = {'Children': 65, 'Adults': 45, 'Elderly': 78, 'Urban': 55, 'Rural': 60}
        return {'conditions': preds, 'region_cards': cards, 'population_risks': pop}

    def detect_nadi_type(self, hrv_ms: float):
        if hrv_ms > 50:
            return 'vata_nadi'
        if hrv_ms >= 30:
            return 'pitta_nadi'
        return 'kapha_nadi'

    def detect_anomaly(self, readings: list):
        if len(readings) < 5:
            return False
        mean = sum(readings) / len(readings)
        var = sum((x - mean) ** 2 for x in readings) / len(readings)
        std = math.sqrt(var)
        return abs(readings[-1] - mean) > 2 * std
import math
import random

class MLService:
    def generate_forecast(self):
        days = list(range(30))
        conds = {"Respiratory": 30, "Digestive": 20, "Fever/Viral": 40, "Skin": 15, "Joint": 25}
        preds = {}
        for c, base in conds.items():
            preds[c] = [round(base + 10 * math.sin(d/5) + random.uniform(-5, 5), 1) for d in days]
        
        cards = [
            {"region": "Maharashtra", "condition": "Fever/Viral", "peak_in_days": 5, "severity": "high"},
            {"region": "Delhi", "condition": "Respiratory", "peak_in_days": 12, "severity": "critical"},
            {"region": "Karnataka", "condition": "Digestive", "peak_in_days": 2, "severity": "medium"},
            {"region": "Kerala", "condition": "Skin", "peak_in_days": 28, "severity": "low"}
        ]
        pop = {"Children": 65, "Adults": 45, "Elderly": 78, "Urban": 55, "Rural": 60}
        return {"conditions": preds, "region_cards": cards, "population_risks": pop}

    def detect_nadi_type(self, hrv_ms: float):
        if hrv_ms > 50: return "vata_nadi"
        if hrv_ms >= 30: return "pitta_nadi"
        return "kapha_nadi"

    def detect_anomaly(self, readings: list):
        if len(readings) < 5: return False
        mean = sum(readings) / len(readings)
        var = sum((x - mean)**2 for x in readings) / len(readings)
        std = math.sqrt(var)
        return abs(readings[-1] - mean) > 2 * std
