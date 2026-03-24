import httpx
from datetime import datetime
from app.config import settings


class WeatherData:
    def __init__(self, temp: float, humidity: float, rainfall: float, aqi: int, condition: str):
        self.temperature = temp
        self.humidity = humidity
        self.rainfall = rainfall
        self.aqi = aqi
        self.condition = condition


class WeatherService:
    async def get_district_weather(self, lat: float, lon: float) -> WeatherData:
        key = settings.OPENWEATHER_API_KEY
        if not key or key == 'YOUR_KEY_HERE':
            return WeatherData(28, 65, 0, 2, 'clear')
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric')
                data = res.json()
                temp = data.get('main', {}).get('temp', 28)
                hum = data.get('main', {}).get('humidity', 65)
                cond = data.get('weather', [{}])[0].get('main', 'clear')
                return WeatherData(temp, hum, 0, 2, cond)
            except Exception:
                return WeatherData(28, 65, 0, 2, 'clear')

    def calculate_climate_risk(self, weather: WeatherData, season: str):
        risks = {'Fever/Viral': 0, 'Respiratory': 0, 'Joint': 0, 'Digestive': 0}
        if weather.humidity > 80 and season == 'monsoon':
            risks['Fever/Viral'] = min(100, weather.humidity * 1.2)
        if weather.aqi >= 3:
            risks['Respiratory'] += weather.aqi * 20
        if weather.temperature < 15:
            risks['Joint'] += (15 - weather.temperature) * 4
            risks['Respiratory'] += 25
        if weather.rainfall > 50:
            risks['Digestive'] += 40
        return risks

    def get_current_season(self):
        m = datetime.now().month
        if m in [12, 1, 2]:
            return 'winter'
        if m in [3, 4, 5]:
            return 'summer'
        if m in [6, 7, 8, 9]:
            return 'monsoon'
        return 'autumn'
import httpx
from datetime import datetime
from app.config import settings

class WeatherData:
    def __init__(self, temp: float, humidity: float, rainfall: float, aqi: int, condition: str):
        self.temperature = temp
        self.humidity = humidity
        self.rainfall = rainfall
        self.aqi = aqi
        self.condition = condition

class WeatherService:
    async def get_district_weather(self, lat: float, lon: float) -> WeatherData:
        key = settings.OPENWEATHER_API_KEY
        if not key or key == "YOUR_KEY_HERE":
            return WeatherData(28, 65, 0, 2, "clear")
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric")
                data = res.json()
                temp = data.get("main", {}).get("temp", 28)
                hum = data.get("main", {}).get("humidity", 65)
                cond = data.get("weather", [{}])[0].get("main", "clear")
                return WeatherData(temp, hum, 0, 2, cond)
            except:
                return WeatherData(28, 65, 0, 2, "clear")

    def calculate_climate_risk(self, weather: WeatherData, season: str):
        risks = {"Fever/Viral": 0, "Respiratory": 0, "Joint": 0, "Digestive": 0}
        if weather.humidity > 80 and season == "monsoon": risks["Fever/Viral"] = min(100, weather.humidity * 1.2)
        if weather.aqi >= 3: risks["Respiratory"] += weather.aqi * 20
        if weather.temperature < 15: 
            risks["Joint"] += (15 - weather.temperature) * 4
            risks["Respiratory"] += 25
        if weather.rainfall > 50: risks["Digestive"] += 40
        return risks

    def get_current_season(self):
        m = datetime.now().month
        if m in [12, 1, 2]: return "winter"
        if m in [3, 4, 5]: return "summer"
        if m in [6, 7, 8, 9]: return "monsoon"
        return "autumn"
