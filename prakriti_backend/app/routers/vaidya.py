from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.prakriti import PrakritiProfile
from app.models.recommendation import RecommendationSession
from app.schemas.schemas import VaidyaSuggestionResponse
from app.dependencies import get_current_user
from app.services.claude_service import ClaudeService

router = APIRouter()
claude = ClaudeService()


@router.get('/patients')
async def patients(search: str = '', current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != 'doctor':
        raise HTTPException(status_code=403, detail='Doctor access only')
    stmt = select(User).where(User.role == 'patient')
    if search:
        stmt = stmt.where(User.display_name.ilike(f'%{search}%'))
    users = await db.scalars(stmt)
    return users.all()


@router.get('/patients/{uid}')
async def patient(uid: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != 'doctor':
        raise HTTPException(status_code=403)
    u = await db.scalar(select(User).where(User.id == uid))
    p = await db.scalar(select(PrakritiProfile).where(PrakritiProfile.user_id == uid).order_by(PrakritiProfile.completed_at.desc()))
    s = await db.scalars(select(RecommendationSession).where(RecommendationSession.user_id == uid).order_by(RecommendationSession.created_at.desc()).limit(5))
    return {'user': u, 'profile': p, 'sessions': s.all()}


@router.post('/suggest', response_model=VaidyaSuggestionResponse)
async def suggest(data: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    symptoms = data.get('symptoms', [])
    dosha = data.get('dosha', 'Vata')
    uid = data.get('patient_uid', '')
    hist_raw = []
    if uid:
        s = await db.scalars(select(RecommendationSession).where(RecommendationSession.user_id == uid).order_by(RecommendationSession.created_at.desc()).limit(3))
        hist_raw = [{'symptoms': h.symptoms, 'response': h.response_json} for h in s.all()]
    return await claude.generate_vaidya_suggestion(symptoms, dosha, hist_raw)


@router.post('/interactions')
async def interactions(data: dict):
    return {'safe': True, 'warnings': [], 'note': 'Herb-drug interaction check requires CCRAS database integration — mock response for demo'}


@router.post('/consult')
async def consult(data: dict, current_user: User = Depends(get_current_user)):
    if current_user.role != 'doctor':
        raise HTTPException(status_code=403)
    return {'status': 'saved', 'consult_id': 'c_mock'}


@router.patch('/outcome/{consult_id}')
async def outcome(consult_id: str, data: dict, current_user: User = Depends(get_current_user)):
    if current_user.role != 'doctor':
        raise HTTPException(status_code=403)
    return {'status': 'updated', 'consult_id': consult_id}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.prakriti import PrakritiProfile
from app.models.recommendation import RecommendationSession
from app.schemas.schemas import VaidyaSuggestionResponse
from app.dependencies import get_current_user
from app.services.claude_service import ClaudeService

router = APIRouter()
claude = ClaudeService()

@router.get("/patients")
async def patients(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db), search: str = ""):
    if current_user.role != "doctor": raise HTTPException(status_code=403, detail="Doctor access only")
    stmt = select(User).where(User.role == 'patient')
    if search: stmt = stmt.where(User.display_name.ilike(f"%{search}%"))
    users = await db.scalars(stmt)
    return users.all()

@router.get("/patients/{uid}")
async def patient(uid: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != "doctor": raise HTTPException(status_code=403)
    u = await db.scalar(select(User).where(User.id == uid))
    p = await db.scalar(select(PrakritiProfile).where(PrakritiProfile.user_id == uid).order_by(PrakritiProfile.completed_at.desc()))
    s = await db.scalars(select(RecommendationSession).where(RecommendationSession.user_id == uid).order_by(RecommendationSession.created_at.desc()).limit(5))
    return {"user": u, "profile": p, "sessions": s.all()}

@router.post("/suggest", response_model=VaidyaSuggestionResponse)
async def suggest(data: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    symptoms = data.get("symptoms", [])
    dosha = data.get("dosha", "Vata")
    uid = data.get("patient_uid", "")
    hist_raw = []
    if uid:
        s = await db.scalars(select(RecommendationSession).where(RecommendationSession.user_id == uid).order_by(RecommendationSession.created_at.desc()).limit(3))
        hist_raw = [{"symptoms": h.symptoms, "response": h.response_json} for h in s]
    return await claude.generate_vaidya_suggestion(symptoms, dosha, hist_raw)

@router.post("/interactions")
async def interactions(data: dict):
    return {"safe": True, "warnings": [], "note": "Herb-drug interaction check requires CCRAS database integration — mock response for demo"}

@router.post("/consult")
async def consult(data: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != "doctor": raise HTTPException(status_code=403)
    # mock saving a consult session mapping
    return {"status": "saved", "consult_id": "c_mock"}

@router.patch("/outcome/{consult_id}")
async def outcome(consult_id: str, data: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != "doctor": raise HTTPException(status_code=403)
    return {"status": "updated", "consult_id": consult_id}
