from datetime import datetime

from app.services.ml_service import MLService
from app.services.weather_service import WeatherService


class HeatmapService:
    def __init__(self):
        self._ml = MLService()
        self._weather = WeatherService()

    def filter_districts(self, districts: list, condition: str | None, season: str | None):
        filtered = districts
        if condition and condition.lower() != 'all':
            filtered = [d for d in filtered if str(d.top_condition).lower() == condition.lower()]
        if season and season.lower() != 'all':
            filtered = [d for d in filtered if isinstance(d.seasons_map, dict) and season.lower() in d.seasons_map]
        return filtered

    async def refresh_risk(self, district, season: str | None = None):
        use_season = season or self._weather.get_current_season()
        weather = await self._weather.get_district_weather(district.latitude or 20.0, district.longitude or 78.0)
        monthly = district.monthly_cases if isinstance(district.monthly_cases, list) else list((district.monthly_cases or {}).values())
        risk = self._ml.calculate_district_risk(
            humidity=weather.humidity,
            rainfall=weather.rainfall,
            aqi=weather.aqi * 50,
            temperature=weather.temperature,
            season=use_season,
            monthly_cases=[int(x) for x in (monthly[:6] or [50, 52, 55])],
        )
        district.risk_score = int(risk['risk_score'])
        district.risk_level = risk['risk_level']
        district.top_condition = risk['top_condition']
        district.trend = risk['trend']
        district.updated_at = datetime.utcnow()
        return district
