class WeatherService:
    async def get_current_season(self, lat: float, lon: float):
        return {"season": "Grishma (Summer)", "temp": 35}\n