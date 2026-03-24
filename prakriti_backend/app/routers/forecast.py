from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db, get_redis
from app.dependencies import get_current_user, success_response, resolve_language
from app.models.district import DistrictRisk
from app.models.user import User
from app.services.forecast_service import ForecastService
from app.services.recommendation_service import RecommendationService
from app.services.ml_service import MLService
from app.services.nlp_service import NLPService
from app.services.pdf_service import PDFService
from app.services.weather_service import WeatherService

router = APIRouter()
logger = logging.getLogger('prakriti_backend')
ml = MLService()
ws = WeatherService()
nlp = NLPService()
recommendation_service = RecommendationService()
pdf = PDFService()
forecast_service = ForecastService()

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


@router.get('/national')
async def national():
    try:
        return success_response(forecast_service.national_forecast(), 'National forecast loaded')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Unable to load national forecast: {exc}')


@router.get('/regions')
async def regions():
    try:
        return success_response(forecast_service.region_cards(), 'Regional forecast loaded')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Unable to load regional forecast: {exc}')


@router.get('/population')
async def population():
    try:
        return success_response(forecast_service.population_risks(), 'Population risks loaded')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Unable to load population risks: {exc}')


@router.get('/seasonal')
async def seasonal(season: str | None = None):
    season_key = (season or ws.get_current_season()).lower()
    details = ADVISORIES.get(season_key, ADVISORIES['autumn'])
    return success_response({
        'season': season_key,
        'advisory': details['advisory'],
        'dosha_impact': details['dosha_impact'],
        'recommendations': details['recommendations'],
    }, 'Seasonal advisory loaded')


@router.get('/explain/{district_id}')
async def explain(district_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        district = (await db.execute(select(DistrictRisk).where(DistrictRisk.state_code == district_id))).scalars().first()
        if not district:
            raise HTTPException(status_code=404, detail='District not found')

        weather_summary, social_summary = await forecast_service.build_explanation_context(district)
        reasons = await recommendation_service.generate_xai_explanation(
            district=district.state_name,
            risk_level=district.risk_level,
            risk_score=float(district.risk_score),
            top_condition=district.top_condition,
            trend=district.trend,
            weather_summary=weather_summary,
            social_summary=social_summary,
            language=resolve_language(request),
        )
        return success_response({'reasons': reasons[:5]}, 'Forecast explanation loaded')
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Unable to explain forecast: {exc}')


@router.post('/bulletin')
async def bulletin(data: dict, request: Request, db: AsyncSession = Depends(get_db)):
    district_id = data.get('district_id', 'MH')
    try:
        district = (await db.execute(select(DistrictRisk).where(DistrictRisk.state_code == district_id))).scalars().first()
        if not district:
            raise HTTPException(status_code=404, detail='District not found')

        weather = await ws.get_district_weather(district.latitude or 20.0, district.longitude or 78.0)
        signal = nlp.get_signal_summary(district.state_code)
        forecast = ml.generate_forecast()
        forecast_summary = f"National trend shows peak pressure in {forecast['region_cards'][0]['region']}"
        weather_summary = f'Temp {weather.temperature}C, humidity {weather.humidity}%, AQI {weather.aqi}'

        bulletin_text = await recommendation_service.generate_bulletin_text(
            district_name=district.state_name,
            risk_level=district.risk_level,
            top_conditions=[district.top_condition],
            forecast_summary=forecast_summary,
            weather_summary=weather_summary,
            social_summary=signal.summary,
            language=resolve_language(request),
        )
        xai = await recommendation_service.generate_xai_explanation(
            district=district.state_name,
            risk_level=district.risk_level,
            risk_score=float(district.risk_score),
            top_condition=district.top_condition,
            trend=district.trend,
            weather_summary=weather_summary,
            social_summary=signal.summary,
            language=resolve_language(request),
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
        return success_response({'pdf_base64': encoded, 'district': district.state_name, 'generated_at': datetime.utcnow().isoformat()}, 'Bulletin generated')
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Unable to generate bulletin: {exc}')


@router.post('/refresh')
async def refresh(current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Admin access required')

    data = ml.generate_forecast()
    redis_client = await get_redis()
    if redis_client is not None:
        try:
            await redis_client.set('forecast:national', str(data), ex=3600)
        except Exception as exc:
            logger.warning('Failed to cache refreshed forecast: %s', exc)
    return success_response({'status': 'refreshed', 'generated_at': datetime.utcnow().isoformat()}, 'Forecast refreshed')
