import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.dependencies import get_current_user, success_response, serialize_user, resolve_language
from app.models.prakriti import PrakritiProfile
from app.models.recommendation import RecommendationSession
from app.models.user import User
from app.models.vaidya import VaidyaConsult
from app.services.recommendation_service import RecommendationService

router = APIRouter()
recommendation_service = RecommendationService()

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
        patients_list = (await db.scalars(stmt)).all()
        return success_response([serialize_user(patient) for patient in patients_list], 'Patients loaded')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Unable to fetch patients: {exc}')


@router.get('/patients/{uid}')
async def patient(uid: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != 'doctor':
        raise HTTPException(status_code=403, detail='Doctor access only')
    try:
        try:
            patient_id = uuid.UUID(uid)
        except ValueError:
            raise HTTPException(status_code=400, detail='Invalid patient id')
        user = await db.scalar(select(User).where(User.id == patient_id))
        if not user:
            raise HTTPException(status_code=404, detail='Patient not found')
        profile = await db.scalar(select(PrakritiProfile).where(PrakritiProfile.user_id == patient_id).order_by(PrakritiProfile.completed_at.desc()))
        sessions = (await db.scalars(select(RecommendationSession).where(RecommendationSession.user_id == patient_id).order_by(RecommendationSession.created_at.desc()).limit(5))).all()
        return success_response({'user': serialize_user(user), 'profile': profile, 'sessions': sessions}, 'Patient details loaded')
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Unable to fetch patient profile: {exc}')


@router.post('/suggest')
async def suggest(data: dict, request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != 'doctor':
        raise HTTPException(status_code=403, detail='Doctor access only')
    symptoms = data.get('symptoms', [])
    dosha = data.get('dosha', 'Vata')
    uid = data.get('patient_uid', '')
    history = []

    try:
        if uid:
            try:
                patient_id = uuid.UUID(uid)
            except ValueError:
                raise HTTPException(status_code=400, detail='Invalid patient id')
            sessions = await db.scalars(select(RecommendationSession).where(RecommendationSession.user_id == patient_id).order_by(RecommendationSession.created_at.desc()).limit(3))
            history = [{'symptoms': s.symptoms, 'response': s.response_json} for s in sessions.all()]
        language = resolve_language(request, current_user.language)
        return success_response(await recommendation_service.generate_vaidya_suggestion(symptoms, dosha, history, language), 'Vaidya suggestion generated')
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Unable to generate vaidya suggestion: {exc}')


@router.get('/evidence')
async def evidence():
    return success_response([
        {'condition': 'acidity', 'success_rate': 78, 'sample_size': 124, 'confidence': 'moderate'},
        {'condition': 'joint pain', 'success_rate': 65, 'sample_size': 162, 'confidence': 'moderate'},
        {'condition': 'insomnia', 'success_rate': 71, 'sample_size': 98, 'confidence': 'emerging'},
        {'condition': 'digestive discomfort', 'success_rate': 74, 'sample_size': 143, 'confidence': 'moderate'},
    ], 'Evidence data fetched')


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

    return success_response({'interactions': matches, 'safe': len(matches) == 0}, 'Interaction analysis complete')


@router.post('/consult')
async def consult(data: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != 'doctor':
        raise HTTPException(status_code=403, detail='Doctor access only')

    patient_uid = str(data.get('patient_uid', '')).strip()
    symptoms_raw = data.get('symptoms', [])
    symptoms = [str(item).strip() for item in symptoms_raw if str(item).strip()] if isinstance(symptoms_raw, list) else []
    suggestion = data.get('suggestion') if isinstance(data.get('suggestion'), dict) else None

    if not patient_uid:
        raise HTTPException(status_code=400, detail='patient_uid is required')

    try:
        patient_id = uuid.UUID(patient_uid)
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid patient id')

    patient = await db.scalar(select(User).where(User.id == patient_id))
    if not patient:
        raise HTTPException(status_code=404, detail='Patient not found')

    consult_row = VaidyaConsult(
        doctor_id=current_user.id,
        patient_id=patient_id,
        symptoms=symptoms,
        suggestion_json=suggestion,
        status='suggested',
    )
    db.add(consult_row)
    await db.commit()
    await db.refresh(consult_row)
    return success_response({'status': 'saved', 'consult_id': str(consult_row.id)}, 'Consult saved')


@router.patch('/outcome/{consult_id}')
async def outcome(consult_id: str, data: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role != 'doctor':
        raise HTTPException(status_code=403, detail='Doctor access only')

    try:
        consult_uuid = uuid.UUID(consult_id)
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid consult id')

    consult_row = await db.scalar(select(VaidyaConsult).where(VaidyaConsult.id == consult_uuid))
    if not consult_row:
        raise HTTPException(status_code=404, detail='Consult not found')

    consult_row.outcome_json = data if isinstance(data, dict) else {'outcome': str(data)}
    consult_row.status = 'completed'
    await db.commit()
    await db.refresh(consult_row)
    return success_response({'status': 'updated', 'consult_id': consult_id, 'outcome': consult_row.outcome_json}, 'Consult outcome updated')

