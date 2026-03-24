from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.hrv import HrvReading
from app.schemas.schemas import WearableReadingRequest, NadiDiagnosisResponse
from app.dependencies import get_current_user
from app.services.ml_service import MLService

router = APIRouter()
ml = MLService()


@router.post('/hrv-sync')
async def hrv_sync(req: WearableReadingRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    saved = 0
    anom = False
    hist_vals = list(await db.scalars(select(HrvReading.hrv_ms).where(HrvReading.user_id == current_user.id).order_by(HrvReading.measured_at.desc()).limit(10)))
    for r in req.readings:
        ms = float(r['hrv_ms'])
        nadi = ml.detect_nadi_type(ms)
        check = hist_vals + [ms]
        anom = ml.detect_anomaly(check)
        rd = HrvReading(user_id=current_user.id, hrv_ms=ms, nadi_type=nadi, is_anomaly=anom)
        db.add(rd)
        saved += 1
    await db.commit()
    return {'saved': saved, 'anomaly_detected': anom}


@router.get('/nadi', response_model=NadiDiagnosisResponse)
async def nadi(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    hist = list(await db.scalars(select(HrvReading).where(HrvReading.user_id == current_user.id).order_by(HrvReading.measured_at.desc()).limit(30)))
    if not hist:
        return {'type': 'Unknown', 'hrv_ms': 0.0, 'stress_index': 0.0, 'is_anomaly': False}
    avg = sum(x.hrv_ms for x in hist) / len(hist)
    t = ml.detect_nadi_type(avg)
    anom = any(x.is_anomaly for x in hist)
    return {'type': t, 'hrv_ms': round(avg, 2), 'stress_index': round(500 / avg if avg > 0 else 100, 2), 'is_anomaly': anom}


@router.get('/trend')
async def trend(days: int = 30, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    hist = list(await db.scalars(select(HrvReading).where(HrvReading.user_id == current_user.id).order_by(HrvReading.measured_at.asc()).limit(days)))
    return [{'date': str(h.measured_at), 'hrv_ms': h.hrv_ms, 'nadi_type': h.nadi_type} for h in hist]


@router.get('/anomalies')
async def anomalies(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    hist = list(await db.scalars(select(HrvReading).where(HrvReading.user_id == current_user.id, HrvReading.is_anomaly == True).order_by(HrvReading.measured_at.desc())))
    return [{'date': str(h.measured_at), 'hrv_ms': h.hrv_ms, 'nadi_type': h.nadi_type} for h in hist]
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.hrv import HrvReading
from app.schemas.schemas import WearableReadingRequest, NadiDiagnosisResponse
from app.dependencies import get_current_user
from app.services.ml_service import MLService
from datetime import datetime, timedelta

router = APIRouter()
ml = MLService()

@router.post("/hrv-sync")
async def hrv_sync(req: WearableReadingRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    readings = []
    saved = 0
    for r in req.readings:
        ms = float(r["hrv_ms"])
        nadi = ml.detect_nadi_type(ms)
        hist = await db.scalars(select(HrvReading.hrv_ms).where(HrvReading.user_id == current_user.id).order_by(HrvReading.measured_at.desc()).limit(10))
        h_arr = list(hist.all())
        h_arr.append(ms)
        anom = ml.detect_anomaly(h_arr)
        
        rd = HrvReading(user_id=current_user.id, hrv_ms=ms, nadi_type=nadi, is_anomaly=anom)
        db.add(rd)
        saved += 1
    await db.commit()
    return {"saved": saved, "anomaly_detected": anom if 'anom' in locals() else False}

@router.get("/nadi", response_model=NadiDiagnosisResponse)
async def nadi(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    hist = await db.scalars(select(HrvReading).where(HrvReading.user_id == current_user.id).order_by(HrvReading.measured_at.desc()).limit(30))
    h_arr = list(hist.all())
    if not h_arr: return {"type": "Unknown", "hrv_ms": 0, "stress_index": 0, "is_anomaly": False}
    avg = sum(x.hrv_ms for x in h_arr) / len(h_arr)
    t = ml.detect_nadi_type(avg)
    anom = any(x.is_anomaly for x in h_arr)
    return {"type": t, "hrv_ms": avg, "stress_index": 500/avg if avg>0 else 100, "is_anomaly": anom}

@router.get("/trend")
async def trend(days: int = 30, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    hist = await db.scalars(select(HrvReading).where(HrvReading.user_id == current_user.id).order_by(HrvReading.measured_at.asc()).limit(30))
    return [{"date": h.measured_at, "hrv_ms": h.hrv_ms, "nadi_type": h.nadi_type} for h in hist.all()]

@router.get("/anomalies")
async def anomalies(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    hist = await db.scalars(select(HrvReading).where(HrvReading.user_id == current_user.id, HrvReading.is_anomaly == True).order_by(HrvReading.measured_at.desc()))
    return [{"date": h.measured_at, "hrv_ms": h.hrv_ms, "nadi_type": h.nadi_type} for h in hist.all()]
