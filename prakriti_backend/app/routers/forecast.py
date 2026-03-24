from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.district import DistrictRisk
from app.schemas.schemas import ForecastResponse
from app.services.ml_service import MLService
from app.services.weather_service import WeatherService
from app.services.nlp_service import NLPService
from app.services.claude_service import ClaudeService
from app.services.pdf_service import PDFService

router = APIRouter()
ml = MLService()
ws = WeatherService()
nlp = NLPService()
claude = ClaudeService()
pdf = PDFService()

ADVISORIES = {
    'winter': 'Consume rich warm oily foods. Protect against dry Vata and Kapha congestion. Sesame oil massage recommended.',
    'summer': 'Stay hydrated, favor cooling foods like cucumber and buttermilk. Minimize Pitta excess. Avoid direct midday sun.',
    'monsoon': 'Drink boiled water, avoid raw foods to prevent Agni sluggishness. Use digestive spices like ginger and cumin.',
    'autumn': 'Balance Pitta spike with moderate grounding foods. Transition to warmer clothing. Favour root vegetables.'
}


@router.get('/national', response_model=ForecastResponse)
async def national():
    return ml.generate_forecast()


@router.get('/regions')
async def regions():
    return ml.generate_forecast()['region_cards']


@router.get('/population')
async def population():
    return ml.generate_forecast()['population_risks']


@router.get('/seasonal')
async def seasonal():
    season = ws.get_current_season()
    return {'season': season, 'advisory': ADVISORIES.get(season, '')}


@router.get('/explain/{district_id}')
async def explain(district_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DistrictRisk).where(DistrictRisk.state_code == district_id))
    d = res.scalars().first()
    if not d:
        return {'reasons': ['District not found. Showing default risk reasoning.']}
    w = await ws.get_district_weather(d.latitude or 12.0, d.longitude or 77.0)
    s = nlp.get_signal_summary(d.state_code)
    weather_summary = f'Temp {w.temperature}C, Humidity {w.humidity}%'
    reasons = await claude.generate_xai_explanation(d.state_name, d.risk_level, d.risk_score, d.top_condition, d.trend, weather_summary, s.summary)
    return {'reasons': reasons}


@router.post('/bulletin')
async def bulletin(data: dict, db: AsyncSession = Depends(get_db)):
    district_id = data.get('district_id', 'MH')
    res = await db.execute(select(DistrictRisk).where(DistrictRisk.state_code == district_id))
    d = res.scalars().first()
    if not d:
        return {'pdf_base64': '', 'district': 'Unknown'}
    w = await ws.get_district_weather(d.latitude or 12.0, d.longitude or 77.0)
    s = nlp.get_signal_summary(d.state_code)
    w_sum = f'Temp {w.temperature}C, Humidity {w.humidity}%'
    xai = await claude.generate_xai_explanation(d.state_name, d.risk_level, d.risk_score, d.top_condition, d.trend, w_sum, s.summary)
    season = ws.get_current_season()
    advisory = ADVISORIES.get(season, '')
    b64 = pdf.generate_bulletin(d.state_name, d.risk_level, d.risk_score, [d.top_condition], xai, advisory)
    return {'pdf_base64': b64, 'district': d.state_name}
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.district import DistrictRisk
from app.schemas.schemas import ForecastResponse
from app.services.ml_service import MLService
from app.services.weather_service import WeatherService
from app.services.nlp_service import NLPService
from app.services.claude_service import ClaudeService
from app.services.pdf_service import PDFService

router = APIRouter()
ml = MLService()
ws = WeatherService()
nlp = NLPService()
claude = ClaudeService()
pdf = PDFService()

@router.get("/national", response_model=ForecastResponse)
async def national():
    return ml.generate_forecast()

@router.get("/regions")
async def regions():
    return ml.generate_forecast()["region_cards"]

@router.get("/population")
async def population():
    return ml.generate_forecast()["population_risks"]

@router.get("/seasonal")
async def seasonal():
    season = ws.get_current_season()
    advisories = {
        "winter": "Consume rich, warm, oily foods. Protect against dry Vata and Kapha congestion.",
        "summer": "Stay hydrated, favor cooling foods like cucumber and buttermilk. Minimize Pitta excess.",
        "monsoon": "Drink boiled water, avoid raw foods to prevent Agni sluggishness.",
        "autumn": "Balance Pitta spike with moderate, grounding foods."
    }
    return {"season": season, "advisory": advisories.get(season, "")}

@router.get("/explain/{district_id}")
async def explain(district_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DistrictRisk).where(DistrictRisk.id == district_id))
    d = res.scalars().first()
    if not d: return {"reasons": ["District not found. Default reason."]}
    w = await ws.get_district_weather(d.latitude, d.longitude)
    s = nlp.get_signal_summary(d.state_code)
    weather_summary = f"Temp {w.temperature}C, Humidity {w.humidity}%"
    reasons = await claude.generate_xai_explanation(d.state_name, d.risk_level, d.risk_score, d.top_condition, d.trend, weather_summary, s.summary)
    return {"reasons": reasons}

@router.post("/bulletin")
async def bulletin(district_id: str, db: AsyncSession = Depends(get_db)):
    d = await db.scalar(select(DistrictRisk).where(DistrictRisk.id == district_id))
    if not d: return {"pdf_base64": "", "district": "Unknown"}
    w = await ws.get_district_weather(d.latitude, d.longitude)
    s = nlp.get_signal_summary(d.state_code)
    w_sum = f"Temp {w.temperature}C"
    xai = await claude.generate_xai_explanation(d.state_name, d.risk_level, d.risk_score, d.top_condition, d.trend, w_sum, s.summary)
    seas = (await seasonal())["advisory"]
    b64 = pdf.generate_bulletin(d.state_name, d.risk_level, d.risk_score, [d.top_condition], xai, seas)
    return {"pdf_base64": b64, "district": d.state_name}
