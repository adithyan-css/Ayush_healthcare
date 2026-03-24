from app.services.ml_service import MLService
from app.services.nlp_service import NLPService
from app.services.weather_service import WeatherService


class ForecastService:
    def __init__(self):
        self._ml = MLService()
        self._nlp = NLPService()
        self._weather = WeatherService()

    def national_forecast(self):
        return self._ml.generate_forecast()

    def region_cards(self):
        return self._ml.generate_forecast()['region_cards']

    def population_risks(self):
        return self._ml.generate_forecast()['population_risks']

    async def build_explanation_context(self, district):
        weather = await self._weather.get_district_weather(district.latitude or 20.0, district.longitude or 78.0)
        signal = self._nlp.get_signal_summary(district.state_code)
        weather_summary = f'Temp {weather.temperature}C, humidity {weather.humidity}%, AQI {weather.aqi}'
        return weather_summary, signal.summary
