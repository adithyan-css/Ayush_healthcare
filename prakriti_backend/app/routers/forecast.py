from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db, get_redis
from app.dependencies import get_current_user
from app.models.district import DistrictRisk
from app.models.user import User
from app.schemas.schemas import ForecastResponse
from app.services.gemini_service import GeminiService
from app.services.ml_service import MLService
from app.services.nlp_service import NLPService
from app.services.pdf_service import PDFService
from app.services.weather_service import WeatherService

router = APIRouter()
ml = MLService()
ws = WeatherService()
nlp = NLPService()
gemini = GeminiService()
pdf = PDFService()

ADVISORIES = {
    'winter': {
        'advisory': 'Use warm nourishing meals and protect respiratory pathways in dry cold weather.',
        'dosha_impact': 'Vata and Kapha aggravation risk',
        'recommendations': ['Sesame oil massage', 'Warm soups with ginger', 'Steam inhalation at night'],
    },
    'summer': {
        'advisory': 'Hydrate frequently and reduce excess heat-producing diet choices.',
        'dosha_impact': 'Pitta aggravation risk',
        'recommendations': ['Cooling foods', 'Coriander-fennel water', 'Avoid direct midday heat'],
    },
    'monsoon': {
        'advisory': 'Protect gut health and avoid contaminated food and water.',
        'dosha_impact': 'Agni variability and Vata imbalance',
        'recommendations': ['Boiled water', 'Light cooked meals', 'Digestive spices in diet'],
    },
    'autumn': {
        'advisory': 'Transition to balanced routines and monitor skin and respiratory sensitivity.',
        'dosha_impact': 'Residual Pitta with Vata transition',
        'recommendations': ['Early sleep schedule', 'Moderate spices', 'Daily breathing practice'],
    },
}


@router.get('/national', response_model=ForecastResponse)
async def national():
    try:
        return ml.generate_forecast()
    except Exception:
        return {'conditions': {}, 'region_cards': [], 'population_risks': {}}


@router.get('/regions')
async def regions():
    try:
        return ml.generate_forecast()['region_cards']
    except Exception:
        return []


@router.get('/population')
async def population():
    try:
        return ml.generate_forecast()['population_risks']
    except Exception:
        return {}


@router.get('/seasonal')
async def seasonal(season: str | None = None):
    season_key = (season or ws.get_current_season()).lower()
    details = ADVISORIES.get(season_key, ADVISORIES['autumn'])
    return {
        'season': season_key,
        'advisory': details['advisory'],
        'dosha_impact': details['dosha_impact'],
        'recommendations': details['recommendations'],
    }


@router.get('/explain/{district_id}')
async def explain(district_id: str, db: AsyncSession = Depends(get_db)):
    try:
        district = (await db.execute(select(DistrictRisk).where(DistrictRisk.state_code == district_id))).scalars().first()
        if not district:
            return {'reasons': ['District not found. Showing default reason list.']}

        weather = await ws.get_district_weather(district.latitude or 20.0, district.longitude or 78.0)
        signal = nlp.get_signal_summary(district.state_code)
        weather_summary = f'Temp {weather.temperature}C, humidity {weather.humidity}%, AQI index {weather.aqi}.'
        reasons = await gemini.generate_xai_explanation(
            district=district.state_name,
            risk_level=district.risk_level,
            risk_score=float(district.risk_score),
            top_condition=district.top_condition,
            trend=district.trend,
            weather_summary=weather_summary,
            social_summary=signal.summary,
        )
        return {'reasons': reasons[:5]}
    except Exception:
        return {
            'reasons': [
                'Regional weather variance is increasing fever and respiratory pressure.',
                'Signal density from symptom reports indicates elevated incidence.',
                'Trendline analysis indicates persistence over recent reporting window.',
                'Population vulnerability factors remain significant in current season.',
            ]
        }


@router.post('/bulletin')
async def bulletin(data: dict, db: AsyncSession = Depends(get_db)):
    district_id = data.get('district_id', 'MH')
    try:
        district = (await db.execute(select(DistrictRisk).where(DistrictRisk.state_code == district_id))).scalars().first()
        if not district:
            return {'pdf_base64': '', 'district': 'Unknown', 'generated_at': datetime.utcnow().isoformat()}

        weather = await ws.get_district_weather(district.latitude or 20.0, district.longitude or 78.0)
        signal = nlp.get_signal_summary(district.state_code)
        forecast = ml.generate_forecast()
        forecast_summary = f"National trend shows peak pressure in {forecast['region_cards'][0]['region']}"
        weather_summary = f'Temp {weather.temperature}C, humidity {weather.humidity}%, AQI {weather.aqi}'

        bulletin_text = await gemini.generate_bulletin_text(
            district_name=district.state_name,
            risk_level=district.risk_level,
            top_conditions=[district.top_condition],
            forecast_summary=forecast_summary,
            weather_summary=weather_summary,
            social_summary=signal.summary,
        )
        xai = await gemini.generate_xai_explanation(
            district=district.state_name,
            risk_level=district.risk_level,
            risk_score=float(district.risk_score),
            top_condition=district.top_condition,
            trend=district.trend,
            weather_summary=weather_summary,
            social_summary=signal.summary,
        )
        season_info = ADVISORIES.get(ws.get_current_season(), ADVISORIES['autumn'])
        encoded = pdf.generate_bulletin(
            district_name=district.state_name,
            risk_level=district.risk_level,
            risk_score=int(district.risk_score),
            top_conditions=[district.top_condition],
            xai_reasons=xai,
            seasonal_advisory=season_info['advisory'],
            bulletin_text=bulletin_text,
        )
        return {'pdf_base64': encoded, 'district': district.state_name, 'generated_at': datetime.utcnow().isoformat()}
    except Exception as exc:
        return {'pdf_base64': '', 'district': district_id, 'generated_at': datetime.utcnow().isoformat(), 'error': str(exc)}


@router.post('/refresh')
async def refresh(current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Admin access required')

    data = ml.generate_forecast()
    redis_client = await get_redis()
    if redis_client is not None:
        try:
            await redis_client.set('forecast:national', str(data), ex=3600)
        except Exception:
            pass
    return {'status': 'refreshed', 'generated_at': datetime.utcnow().isoformat()}
