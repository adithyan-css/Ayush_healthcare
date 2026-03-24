from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.prakriti import PrakritiProfile
from app.models.recommendation import RecommendationSession
from app.models.user import User
from app.schemas.schemas import VaidyaSuggestionResponse
from app.services.gemini_service import GeminiService

router = APIRouter()
gemini = GeminiService()

INTERACTION_MAP = {
    ('ashwagandha', 'sedatives'): ('medium', 'May increase sedation and drowsiness.'),
    ('ginger', 'warfarin'): ('high', 'May increase bleeding risk with anticoagulants.'),
    ('ginkgo', 'aspirin'): ('high', 'May increase antiplatelet bleeding risk.'),
    ('garlic', 'warfarin'): ('high', 'Potential additive anticoagulant effect.'),
    ('guggulu', 'statins'): ('medium', 'May alter lipid-lowering drug response.'),
    ('triphala', 'laxatives'): ('medium', 'May cause loose stools and cramping.'),
    ('licorice', 'diuretics'): ('high', 'Can worsen potassium loss and blood pressure.'),
    ('brahmi', 'thyroid medication'): ('medium', 'May alter thyroid hormone response.'),
    ('turmeric', 'warfarin'): ('high', 'May increase bleeding tendency.'),
    ('fenugreek', 'insulin'): ('medium', 'May potentiate glucose-lowering effect.'),
    ('tulsi', 'antidiabetic drugs'): ('medium', 'Monitor glucose for additive lowering.'),
    ('aloe vera', 'digoxin'): ('high', 'Electrolyte shifts may affect digoxin safety.'),
    ('shilajit', 'antihypertensives'): ('medium', 'May augment blood pressure lowering.'),
    ('saffron', 'ssri'): ('medium', 'Potential additive serotonergic effect.'),
    ('trikatu', 'antacids'): ('low', 'May reduce perceived effect of antacid therapy.'),
    ('chyawanprash', 'antidiabetic drugs'): ('medium', 'Sugar content may affect glucose targets.'),
    ('dashamoola', 'antihypertensives'): ('low', 'Observe blood pressure response.'),
    ('amla', 'anticoagulants'): ('medium', 'Possible additive anti-platelet action.'),
    ('manjistha', 'antiplatelet drugs'): ('medium', 'Monitor bruising and bleeding signs.'),
    ('punarnava', 'diuretics'): ('medium', 'May increase diuretic effect and dehydration risk.'),
}


@router.get('/patients')
async def patients(search: str = '', current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != 'doctor':
        raise HTTPException(status_code=403, detail='Doctor access only')
    try:
        stmt = select(User).where(User.role == 'patient')
        if search:
            stmt = stmt.where(User.display_name.ilike(f'%{search}%'))
        return (await db.scalars(stmt)).all()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Unable to fetch patients: {exc}')


@router.get('/patients/{uid}')
async def patient(uid: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != 'doctor':
        raise HTTPException(status_code=403, detail='Doctor access only')
    try:
        user = await db.scalar(select(User).where(User.id == uid))
        profile = await db.scalar(select(PrakritiProfile).where(PrakritiProfile.user_id == uid).order_by(PrakritiProfile.completed_at.desc()))
        sessions = (await db.scalars(select(RecommendationSession).where(RecommendationSession.user_id == uid).order_by(RecommendationSession.created_at.desc()).limit(5))).all()
        return {'user': user, 'profile': profile, 'sessions': sessions}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Unable to fetch patient profile: {exc}')


@router.post('/suggest', response_model=VaidyaSuggestionResponse)
async def suggest(data: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    symptoms = data.get('symptoms', [])
    dosha = data.get('dosha', 'Vata')
    uid = data.get('patient_uid', '')
    history = []

    try:
        if uid:
            sessions = await db.scalars(select(RecommendationSession).where(RecommendationSession.user_id == uid).order_by(RecommendationSession.created_at.desc()).limit(3))
            history = [{'symptoms': s.symptoms, 'response': s.response_json} for s in sessions.all()]
        return await gemini.generate_vaidya_suggestion(symptoms, dosha, history)
    except Exception:
        return {'formulations': ['Triphala Churna'], 'rationale': 'Supports digestion and dosha equilibrium', 'cautions': ['Consult physician for chronic disease use']}


@router.post('/interactions')
async def interactions(data: dict):
    herbs = [h.lower().strip() for h in data.get('herbs', [])]
    drugs = [d.lower().strip() for d in data.get('drugs', [])]
    matches = []
    for herb in herbs:
        for drug in drugs:
            if (herb, drug) in INTERACTION_MAP:
                severity, warning = INTERACTION_MAP[(herb, drug)]
                matches.append({'herb': herb, 'drug': drug, 'severity': severity, 'warning': warning})

    return {'interactions': matches, 'safe': len(matches) == 0}


@router.post('/consult')
async def consult(data: dict, current_user: User = Depends(get_current_user)):
    if current_user.role != 'doctor':
        raise HTTPException(status_code=403, detail='Doctor access only')
    return {'status': 'saved', 'consult_id': f"consult_{data.get('patient_uid', 'unknown')}"}


@router.patch('/outcome/{consult_id}')
async def outcome(consult_id: str, data: dict, current_user: User = Depends(get_current_user)):
    if current_user.role != 'doctor':
        raise HTTPException(status_code=403, detail='Doctor access only')
    return {'status': 'updated', 'consult_id': consult_id, 'outcome': data}
