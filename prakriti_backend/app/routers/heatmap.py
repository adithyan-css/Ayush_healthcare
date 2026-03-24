from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.database import get_db
from app.schemas.schemas import DistrictRiskResponse
from app.models.district import DistrictRisk
from app.services.weather_service import WeatherService
from app.services.ml_service import MLService

router = APIRouter()
ws = WeatherService()
ml = MLService()

STATES = [
    ('MH', 'Maharashtra', 'Fever/Viral', 72, 'rising', 19.07, 72.87),
    ('KA', 'Karnataka', 'Respiratory', 55, 'stable', 15.31, 75.71),
    ('TN', 'Tamil Nadu', 'Digestive', 48, 'falling', 11.12, 78.65),
    ('DL', 'Delhi', 'Respiratory', 85, 'rising', 28.70, 77.10),
    ('UP', 'Uttar Pradesh', 'Fever/Viral', 63, 'rising', 26.85, 80.99),
    ('WB', 'West Bengal', 'Skin', 44, 'stable', 22.98, 87.85),
    ('GJ', 'Gujarat', 'Joint', 38, 'falling', 22.25, 71.19),
    ('RJ', 'Rajasthan', 'Respiratory', 41, 'stable', 27.02, 74.21),
    ('KL', 'Kerala', 'Fever/Viral', 57, 'rising', 10.85, 76.27),
    ('AP', 'Andhra Pradesh', 'Digestive', 50, 'stable', 15.91, 79.74)
]


def risk_level(score):
    if score >= 75:
        return 'critical'
    if score >= 50:
        return 'high'
    if score >= 25:
        return 'medium'
    return 'low'


async def seed_districts(db: AsyncSession):
    count = await db.scalar(select(func.count()).select_from(DistrictRisk))
    if count == 0:
        monthly = {'Jan': 10, 'Feb': 20, 'Mar': 15, 'Apr': 30, 'May': 25, 'Jun': 40}
        seasons = {'winter': 'Respiratory', 'summer': 'Digestive', 'monsoon': 'Fever/Viral', 'autumn': 'Joint'}
        for code, name, cond, score, trend, lat, lng in STATES:
            dr = DistrictRisk(state_code=code, state_name=name, risk_score=score, risk_level=risk_level(score), top_condition=cond, trend=trend, monthly_cases=monthly, seasons_map=seasons, latitude=lat, longitude=lng)
            db.add(dr)
        await db.commit()


@router.get('/districts', response_model=list[DistrictRiskResponse])
async def get_districts(condition: str = None, season: str = None, db: AsyncSession = Depends(get_db)):
    await seed_districts(db)
    stmt = select(DistrictRisk)
    if condition and condition != 'all':
        stmt = stmt.where(DistrictRisk.top_condition == condition)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get('/state/{state_id}', response_model=DistrictRiskResponse)
async def get_state(state_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DistrictRisk).where(DistrictRisk.state_code == state_id))
    state = res.scalars().first()
    if not state:
        raise HTTPException(status_code=404)
    return state


@router.get('/trend/{state_id}')
async def get_trend(state_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DistrictRisk).where(DistrictRisk.state_code == state_id))
    state = res.scalars().first()
    if not state:
        raise HTTPException(status_code=404)
    return {'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], 'cases': list(state.monthly_cases.values())}


@router.get('/rising', response_model=list[DistrictRiskResponse])
async def get_rising(limit: int = 5, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DistrictRisk).where(DistrictRisk.trend == 'rising').limit(limit))
    return res.scalars().all()


@router.post('/refresh')
async def refresh(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DistrictRisk))
    districts = res.scalars().all()
    for d in districts:
        w = await ws.get_district_weather(d.latitude or 12.0, d.longitude or 77.0)
        s = ws.get_current_season()
        risks = ws.calculate_climate_risk(w, s)
        d.risk_score = min(max(sum(risks.values()) / 4, 10), 100)
        d.risk_level = risk_level(d.risk_score)
    await db.commit()
    return {'updated': len(districts)}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import sqlalchemy as sa
from app.database import get_db
from app.schemas.schemas import DistrictRiskResponse
from app.models.district import DistrictRisk
from app.services.weather_service import WeatherService
from app.services.ml_service import MLService
import random

router = APIRouter()
ws = WeatherService()
ml = MLService()

@router.on_event("startup")
async def seed_districts():
    async for db in get_db():
        count = await db.scalar(select(sa.func.count()).select_from(DistrictRisk))
        if count == 0:
            states = ["MH", "KA", "TN", "DL", "UP", "WB", "GJ", "RJ", "KL", "AP"]
            for s in states:
                dr = DistrictRisk(state_code=s, state_name=f"State {s}", risk_score=random.uniform(20, 80), risk_level="Medium", top_condition="Fever", trend="stable", monthly_cases={"Jan":10, "Feb": 20}, seasons_map={"winter":"High"}, latitude=12.9, longitude=77.5)
                db.add(dr)
            await db.commit()
        break

@router.get("/districts", response_model=list[DistrictRiskResponse])
async def get_districts(condition: str = None, season: str = None, db: AsyncSession = Depends(get_db)):
    stmt = select(DistrictRisk)
    if condition: stmt = stmt.where(DistrictRisk.top_condition == condition)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/state/{state_id}", response_model=DistrictRiskResponse)
async def get_state(state_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DistrictRisk).where(DistrictRisk.state_code == state_id))
    state = res.scalars().first()
    if not state: raise HTTPException(status_code=404)
    return state

@router.get("/trend/{state_id}")
async def get_trend(state_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DistrictRisk).where(DistrictRisk.state_code == state_id))
    state = res.scalars().first()
    if not state: raise HTTPException(status_code=404)
    return {"months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"], "cases": [10, 20, 15, 30, 25, 40]}

@router.get("/rising", response_model=list[DistrictRiskResponse])
async def get_rising(limit: int = 5, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DistrictRisk).where(DistrictRisk.trend == 'rising').limit(limit))
    return res.scalars().all()

@router.post("/refresh")
async def refresh(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(DistrictRisk))
    districts = res.scalars().all()
    count = 0
    for d in districts: # mock update
        w = await ws.get_district_weather(d.latitude or 12.0, d.longitude or 77.0)
        s = ws.get_current_season()
        risks = ws.calculate_climate_risk(w, s)
        d.risk_score = min(max(sum(risks.values()) / 4, 10), 100)
        count += 1
    await db.commit()
    return {"updated": count}
