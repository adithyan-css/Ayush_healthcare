import math


class MLService:
    def generate_forecast(self):
        days = list(range(30))
        bases = {'Respiratory': 48, 'Digestive': 38, 'Fever/Viral': 56, 'Skin': 34, 'Joint': 42}
        phases = {'Respiratory': 0.3, 'Digestive': 1.1, 'Fever/Viral': 0.7, 'Skin': 1.7, 'Joint': 2.2}
        amplitudes = {'Respiratory': 11, 'Digestive': 8, 'Fever/Viral': 13, 'Skin': 7, 'Joint': 10}

        conditions: dict[str, list[float]] = {}
        for condition, base in bases.items():
            series = []
            for day in days:
                harmonic = amplitudes[condition] * math.sin((day / 4.8) + phases[condition])
                drift = 0.18 * day if condition in {'Respiratory', 'Fever/Viral'} else 0.08 * day
                value = max(8.0, min(96.0, round(base + harmonic + drift, 1)))
                series.append(value)
            conditions[condition] = series

        region_cards = [
            {'region': 'Maharashtra', 'condition': 'Fever/Viral', 'peak_in_days': 6, 'severity': 'high', 'trajectory': 'rising'},
            {'region': 'Delhi', 'condition': 'Respiratory', 'peak_in_days': 10, 'severity': 'critical', 'trajectory': 'rising'},
            {'region': 'Tamil Nadu', 'condition': 'Digestive', 'peak_in_days': 4, 'severity': 'medium', 'trajectory': 'stable'},
            {'region': 'Kerala', 'condition': 'Skin', 'peak_in_days': 22, 'severity': 'low', 'trajectory': 'falling'},
        ]
        population_risks = {'Children': 67, 'Adults': 49, 'Elderly': 79, 'Urban': 58, 'Rural': 54}
        return {'conditions': conditions, 'region_cards': region_cards, 'population_risks': population_risks}

    def detect_nadi_type(self, hrv_ms: float):
        if hrv_ms > 50:
            return 'vata_nadi'
        if 30 <= hrv_ms <= 50:
            return 'pitta_nadi'
        return 'kapha_nadi'

    def detect_anomaly(self, readings: list[float]):
        if len(readings) < 5:
            return False
        mean = sum(readings) / len(readings)
        variance = sum((x - mean) ** 2 for x in readings) / len(readings)
        std_dev = math.sqrt(variance)
        return abs(readings[-1] - mean) > (2 * std_dev)

    def calculate_district_risk(
        self,
        humidity: float,
        rainfall: float,
        aqi: int,
        temperature: float,
        season: str,
        monthly_cases: list[int],
    ):
        risk_total = 18
        fever_viral = 20
        respiratory = 20
        digestive = 18
        skin = 15
        joint = 17

        if humidity > 80 and season == 'monsoon':
            fever_viral += 24
            risk_total += 16
        if rainfall > 80:
            fever_viral += 10
            digestive += 8
            risk_total += 8
        if aqi > 150:
            respiratory += 26
            risk_total += 18
        elif aqi > 100:
            respiratory += 14
            risk_total += 9
        if temperature < 15:
            joint += 20
            respiratory += 10
            risk_total += 12
        if temperature > 38:
            skin += 16
            digestive += 10
            risk_total += 10

        trend = 'stable'
        if len(monthly_cases) >= 3 and monthly_cases[-1] > monthly_cases[-2] > monthly_cases[-3]:
            trend = 'rising'
            risk_total += 8
        elif len(monthly_cases) >= 3 and monthly_cases[-1] < monthly_cases[-2] < monthly_cases[-3]:
            trend = 'falling'

        condition_scores = {
            'Fever/Viral': fever_viral,
            'Respiratory': respiratory,
            'Digestive': digestive,
            'Skin': skin,
            'Joint': joint,
        }
        top_condition = max(condition_scores, key=condition_scores.get)
        risk_score = int(max(0, min(100, round(risk_total))))
        if risk_score >= 75:
            risk_level = 'critical'
        elif risk_score >= 50:
            risk_level = 'high'
        elif risk_score >= 25:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'top_condition': top_condition,
            'trend': trend,
        }
