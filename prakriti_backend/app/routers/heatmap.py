from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.district import DistrictRisk
from app.models.user import User
from app.schemas.schemas import DistrictRiskResponse
from app.services.ml_service import MLService
from app.services.weather_service import WeatherService

router = APIRouter()
ws = WeatherService()
ml = MLService()


def _risk_level(score: int) -> str:
    if score >= 75:
        return 'critical'
    if score >= 50:
        return 'high'
    if score >= 25:
        return 'medium'
    return 'low'


async def _ensure_seeded(db: AsyncSession) -> None:
    count = await db.scalar(select(func.count()).select_from(DistrictRisk))
    if (count or 0) > 0:
        return
    states = [
        ('MH', 'Maharashtra', 71, 'Fever/Viral', 'rising', [120, 134, 142, 160, 181, 205], 19.0760, 72.8777),
        ('DL', 'Delhi', 82, 'Respiratory', 'rising', [140, 152, 169, 183, 196, 222], 28.6139, 77.2090),
        ('TN', 'Tamil Nadu', 49, 'Digestive', 'stable', [88, 92, 95, 97, 98, 102], 13.0827, 80.2707),
        ('KA', 'Karnataka', 56, 'Respiratory', 'stable', [96, 102, 109, 115, 119, 125], 12.9716, 77.5946),
        ('KL', 'Kerala', 58, 'Fever/Viral', 'rising', [90, 101, 114, 128, 141, 149], 8.5241, 76.9366),
        ('RJ', 'Rajasthan', 42, 'Joint', 'stable', [72, 74, 75, 78, 81, 83], 26.9124, 75.7873),
        ('UP', 'Uttar Pradesh', 63, 'Fever/Viral', 'rising', [122, 130, 141, 155, 170, 188], 26.8467, 80.9462),
        ('WB', 'West Bengal', 46, 'Skin', 'stable', [86, 88, 92, 94, 96, 99], 22.5726, 88.3639),
        ('GJ', 'Gujarat', 39, 'Joint', 'falling', [98, 95, 91, 88, 84, 81], 23.0225, 72.5714),
        ('PB', 'Punjab', 52, 'Respiratory', 'rising', [89, 93, 98, 104, 112, 121], 30.9010, 75.8573),
    ]
    seasons = {'winter': 'Respiratory', 'summer': 'Digestive', 'monsoon': 'Fever/Viral', 'autumn': 'Joint'}
    for code, name, score, condition, trend, monthly, lat, lng in states:
        db.add(
            DistrictRisk(
                state_code=code,
                state_name=name,
                risk_score=score,
                risk_level=_risk_level(score),
                top_condition=condition,
                trend=trend,
                monthly_cases=monthly,
                seasons_map=seasons,
                latitude=lat,
                longitude=lng,
            )
        )
    await db.commit()


@router.get('/districts', response_model=list[DistrictRiskResponse])
async def get_districts(condition: str | None = None, season: str | None = None, db: AsyncSession = Depends(get_db)):
    try:
        await _ensure_seeded(db)
        stmt = select(DistrictRisk)
        if condition and condition != 'all':
            stmt = stmt.where(DistrictRisk.top_condition == condition)
        rows = (await db.execute(stmt.order_by(DistrictRisk.risk_score.desc()))).scalars().all()
        return rows
    except Exception:
        return []


@router.get('/state/{state_id}', response_model=DistrictRiskResponse)
async def get_state(state_id: str, db: AsyncSession = Depends(get_db)):
    try:
        await _ensure_seeded(db)
        row = (await db.execute(select(DistrictRisk).where(DistrictRisk.state_code == state_id))).scalars().first()
        if not row:
            raise HTTPException(status_code=404, detail='State not found')
        return row
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Unable to fetch state detail: {exc}')


@router.get('/trend/{state_id}')
async def get_trend(state_id: str, db: AsyncSession = Depends(get_db)):
    try:
        await _ensure_seeded(db)
        row = (await db.execute(select(DistrictRisk).where(DistrictRisk.state_code == state_id))).scalars().first()
        if not row:
            raise HTTPException(status_code=404, detail='State not found')
        monthly = row.monthly_cases if isinstance(row.monthly_cases, list) else list(row.monthly_cases.values())
        return {'months': ['M1', 'M2', 'M3', 'M4', 'M5', 'M6'], 'cases': monthly[:6]}
    except HTTPException:
        raise
    except Exception:
        return {'months': ['M1', 'M2', 'M3', 'M4', 'M5', 'M6'], 'cases': [60, 64, 70, 75, 82, 91]}


@router.get('/rising', response_model=list[DistrictRiskResponse])
async def get_rising(limit: int = 5, db: AsyncSession = Depends(get_db)):
    try:
        await _ensure_seeded(db)
        stmt = select(DistrictRisk).where(DistrictRisk.trend == 'rising').order_by(DistrictRisk.risk_score.desc()).limit(limit)
        return (await db.execute(stmt)).scalars().all()
    except Exception:
        return []


@router.post('/refresh')
async def refresh(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Admin access required')

    try:
        await _ensure_seeded(db)
        rows = (await db.execute(select(DistrictRisk))).scalars().all()
        updated = 0
        season = ws.get_current_season()
        for row in rows:
            weather = await ws.get_district_weather(row.latitude or 20.0, row.longitude or 78.0)
            monthly = row.monthly_cases if isinstance(row.monthly_cases, list) else list(row.monthly_cases.values())
            risk = ml.calculate_district_risk(
                humidity=weather.humidity,
                rainfall=weather.rainfall,
                aqi=weather.aqi * 50,
                temperature=weather.temperature,
                season=season,
                monthly_cases=[int(x) for x in monthly[:6]] if monthly else [50, 52, 55],
            )
            row.risk_score = int(risk['risk_score'])
            row.risk_level = risk['risk_level']
            row.top_condition = risk['top_condition']
            row.trend = risk['trend']
            row.updated_at = datetime.utcnow()
            updated += 1
        await db.commit()
        return {'updated': updated, 'timestamp': datetime.utcnow().isoformat()}
    except Exception as exc:
        await db.rollback()
        return {'updated': 0, 'timestamp': datetime.utcnow().isoformat(), 'error': str(exc)}
