from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.dependencies import get_current_user, success_response
from app.models.hrv import HrvReading
from app.models.user import User
from app.schemas.schemas import NadiDiagnosisResponse, WearableReadingRequest
from app.services.wearable_service import WearableService

router = APIRouter()
wearable_service = WearableService()


@router.post('/hrv-sync')
async def hrv_sync(req: WearableReadingRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        saved = 0
        anomaly_detected = False

        hist_vals = list(
            await db.scalars(
                select(HrvReading.hrv_ms)
                .where(HrvReading.user_id == current_user.id)
                .order_by(HrvReading.measured_at.desc())
                .limit(10)
            )
        )

        for reading in req.readings:
            ms = float(reading['hrv_ms'])
            nadi = wearable_service.detect_nadi(ms)
            check = hist_vals + [ms]
            anomaly_detected = wearable_service.is_anomaly(check)

            row = HrvReading(
                user_id=current_user.id,
                hrv_ms=ms,
                nadi_type=nadi,
                is_anomaly=anomaly_detected,
            )
            db.add(row)
            saved += 1

        await db.commit()
        return success_response({'saved': saved, 'anomaly_detected': anomaly_detected}, 'HRV readings synced')
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f'Unable to sync HRV readings: {exc}')


@router.get('/nadi')
async def nadi(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        hist = list(
            await db.scalars(
                select(HrvReading)
                .where(HrvReading.user_id == current_user.id)
                .order_by(HrvReading.measured_at.desc())
                .limit(30)
            )
        )
        if not hist:
            return success_response({'type': 'Unknown', 'hrv_ms': 0.0, 'stress_index': 0.0, 'is_anomaly': False}, 'Nadi summary loaded')

        return success_response(
            wearable_service.build_nadi_summary(
                readings=[item.hrv_ms for item in hist],
                anomaly_flags=[item.is_anomaly for item in hist],
            ),
            'Nadi summary loaded',
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Unable to load nadi summary: {exc}')


@router.get('/trend')
async def trend(days: int = 30, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        hist = list(
            await db.scalars(
                select(HrvReading)
                .where(HrvReading.user_id == current_user.id)
                .order_by(HrvReading.measured_at.asc())
                .limit(days)
            )
        )
        return success_response([{'date': str(item.measured_at), 'hrv_ms': item.hrv_ms, 'nadi_type': item.nadi_type} for item in hist], 'HRV trend loaded')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Unable to load HRV trend: {exc}')


@router.get('/anomalies')
async def anomalies(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        hist = list(
            await db.scalars(
                select(HrvReading)
                .where(HrvReading.user_id == current_user.id, HrvReading.is_anomaly == True)
                .order_by(HrvReading.measured_at.desc())
            )
        )
        return success_response([{'date': str(item.measured_at), 'hrv_ms': item.hrv_ms, 'nadi_type': item.nadi_type} for item in hist], 'Anomalies loaded')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Unable to load anomalies: {exc}')
