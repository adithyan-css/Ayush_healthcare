from dataclasses import dataclass
from datetime import datetime
import httpx
from app.config import settings


@dataclass
class WeatherData:
    temperature: float
    humidity: float
    rainfall: float
    aqi: int
    condition: str
    uv_index: float


class WeatherService:
    async def get_district_weather(self, lat: float, lng: float) -> WeatherData:
        key = settings.OPENWEATHER_API_KEY
        if key:
            try:
                async with httpx.AsyncClient(timeout=8.5) as client:
                    weather_res = await client.get(
                        f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={key}&units=metric'
                    )
                    weather_res.raise_for_status()
                    weather = weather_res.json()

                    air_res = await client.get(
                        f'https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lng}&appid={key}'
                    )
                    air_res.raise_for_status()
                    air = air_res.json()

                    temperature = float(weather.get('main', {}).get('temp', 30.0))
                    humidity = float(weather.get('main', {}).get('humidity', 60.0))
                    rainfall = float(weather.get('rain', {}).get('1h', weather.get('rain', {}).get('3h', 0.0)))
                    aqi = int(air.get('list', [{}])[0].get('main', {}).get('aqi', 2))
                    condition = str(weather.get('weather', [{}])[0].get('main', 'Clear'))
                    uv_index = 6.0
                    return WeatherData(temperature, humidity, rainfall, aqi, condition, uv_index)
            except Exception:
                pass

        month = datetime.now().month
        if lat < 15:
            base_temp, base_humidity = 32.0, 76.0
        elif lat <= 25:
            base_temp, base_humidity = 29.0, 66.0
        else:
            base_temp, base_humidity = 24.0, 58.0

        if month in [6, 7, 8, 9]:
            rainfall, humidity_delta, temp_delta, condition = 18.0, 14.0, -2.0, 'Rain'
        elif month in [12, 1, 2]:
            rainfall, humidity_delta, temp_delta, condition = 2.0, -5.0, -5.0, 'Haze'
        elif month in [3, 4, 5]:
            rainfall, humidity_delta, temp_delta, condition = 1.0, -6.0, 4.0, 'Clear'
        else:
            rainfall, humidity_delta, temp_delta, condition = 4.0, 0.0, 0.5, 'Clouds'

        temperature = base_temp + temp_delta
        humidity = max(30.0, min(95.0, base_humidity + humidity_delta))
        aqi = 4 if lat > 26 and month in [11, 12, 1] else 2
        uv_index = 8.5 if month in [4, 5, 6] else 5.2
        return WeatherData(temperature, humidity, rainfall, aqi, condition, uv_index)

    def get_current_season(self):
        month = datetime.now().month
        if month in [6, 7, 8, 9]:
            return 'monsoon'
        if month in [12, 1, 2]:
            return 'winter'
        if month in [3, 4, 5]:
            return 'summer'
        return 'autumn'

    def calculate_climate_disease_risk(self, weather: WeatherData, season: str):
        risks = {'Fever/Viral': 18, 'Respiratory': 20, 'Joint': 15, 'Digestive': 17, 'Skin': 14}
        if weather.humidity > 80 and season == 'monsoon':
            risks['Fever/Viral'] += 28
        if weather.aqi >= 3:
            risks['Respiratory'] += weather.aqi * 14
        if weather.temperature < 15:
            risks['Joint'] += 24
            risks['Respiratory'] += 11
        if weather.temperature > 38:
            risks['Skin'] += 20
            risks['Digestive'] += 13
        if weather.rainfall > 40:
            risks['Digestive'] += 15
        return {k: int(max(0, min(100, round(v)))) for k, v in risks.items()}
