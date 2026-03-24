from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.dependencies import get_current_user, success_response
from app.models.symptom import SymptomReport
from app.models.user import User
from app.schemas.schemas import SymptomReportRequest

router = APIRouter()


@router.post('/report')
async def report(req: SymptomReportRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sr = SymptomReport(
        user_id=current_user.id,
        symptoms={'items': req.symptoms},
        latitude=req.latitude,
        longitude=req.longitude,
    )
    db.add(sr)
    await db.commit()
    return success_response({}, 'Symptoms logged')


@router.get('/community')
async def community(days: int = 7, db: AsyncSession = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(days=max(days, 1))
    rows = await db.scalars(
        select(SymptomReport)
        .where(SymptomReport.created_at >= since)
        .order_by(SymptomReport.created_at.desc())
        .limit(300)
    )
    counter = Counter()
    for report_row in rows.all():
        for item in report_row.symptoms.get('items', []):
            counter[item] += 1

    top = counter.most_common(10)
    return success_response([{'symptom': symptom, 'count': count, 'trend': 'up'} for symptom, count in top], 'Community symptoms loaded')


@router.get('/clusters')
async def clusters(days: int = 7, db: AsyncSession = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(days=max(days, 1))
    rows = await db.scalars(
        select(SymptomReport)
        .where(SymptomReport.created_at >= since)
        .order_by(SymptomReport.created_at.desc())
        .limit(500)
    )
    reports = rows.all()

    if not reports:
        return success_response({
            'clusters': [
                {'region': 'Indiranagar', 'condition': 'Allergic Rhinitis', 'risk': 'Medium'},
                {'region': 'Whitefield', 'condition': 'Heat Fatigue', 'risk': 'Low'},
            ]
        }, 'Clusters loaded')

    grid_groups = defaultdict(Counter)
    for report_row in reports:
        lat = report_row.latitude
        lon = report_row.longitude
        region = 'Unknown'
        if lat is not None and lon is not None:
            region = f'{round(lat, 1)},{round(lon, 1)}'
        for symptom in report_row.symptoms.get('items', []):
            grid_groups[region][symptom] += 1

    clustered = []
    for region, symptom_counts in grid_groups.items():
        condition, count = symptom_counts.most_common(1)[0]
        risk = 'High' if count >= 8 else 'Medium' if count >= 4 else 'Low'
        clustered.append({'region': region, 'condition': condition, 'risk': risk})

    return success_response({'clusters': clustered[:12]}, 'Clusters loaded')


@router.get('/trending')
async def trending(days: int = 7, db: AsyncSession = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(days=max(days, 1))
    rows = await db.scalars(
        select(SymptomReport)
        .where(SymptomReport.created_at >= since)
        .order_by(SymptomReport.created_at.desc())
        .limit(600)
    )

    counter = Counter()
    for report_row in rows.all():
        for symptom in report_row.symptoms.get('items', []):
            counter[symptom] += 1

    return success_response({
        'days': max(days, 1),
        'top': [{'symptom': symptom, 'count': count} for symptom, count in counter.most_common(5)],
    }, 'Trending symptoms loaded')
