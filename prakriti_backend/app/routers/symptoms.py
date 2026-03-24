from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.symptom import SymptomReport
from app.schemas.schemas import SymptomReportRequest
from app.dependencies import get_current_user

router = APIRouter()


@router.post('/report')
async def report(req: SymptomReportRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sr = SymptomReport(user_id=current_user.id, symptoms={'items': req.symptoms}, latitude=req.latitude, longitude=req.longitude)
    db.add(sr)
    await db.commit()
    return {'status': 'success', 'message': 'Symptoms logged'}


@router.get('/community')
async def community(days: int = 7, db: AsyncSession = Depends(get_db)):
    s = await db.scalars(select(SymptomReport).order_by(SymptomReport.created_at.desc()).limit(200))
    c_dict = {}
    for r in s.all():
        for item in r.symptoms.get('items', []):
            c_dict[item] = c_dict.get(item, 0) + 1
    top = sorted(c_dict.items(), key=lambda x: -x[1])[:10]
    return [{'symptom': k, 'count': v, 'trend': 'up'} for k, v in top]


@router.get('/clusters')
async def clusters():
    return {'clusters': [{'region': 'Indiranagar', 'condition': 'Vata allergy', 'risk': 'Medium'}]}
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.symptom import SymptomReport
from app.schemas.schemas import SymptomReportRequest
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/report")
async def report(req: SymptomReportRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sr = SymptomReport(user_id=current_user.id, symptoms={"items": req.symptoms}, latitude=req.latitude, longitude=req.longitude)
    db.add(sr)
    await db.commit()
    return {"status": "success", "message": "Symptoms logged"}

@router.get("/community")
async def community(db: AsyncSession = Depends(get_db)):
    s = await db.scalars(select(SymptomReport).order_by(SymptomReport.created_at.desc()).limit(100))
    cDict = {}
    for r in s:
        for item in r.symptoms.get("items", []):
            cDict[item] = cDict.get(item, 0) + 1
    top = sorted(cDict.items(), key=lambda x: -x[1])[:10]
    return [{"symptom": k, "count": v, "trend": "up"} for k,v in top]

@router.get("/clusters")
async def clusters(db: AsyncSession = Depends(get_db)):
    return {"clusters": [{"region": "Indiranagar", "condition": "Vata allergy", "risk": "Medium"}]}
