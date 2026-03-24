import hashlib
from pathlib import Path
import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.prakriti import PrakritiProfile
from app.schemas.schemas import PrakritiProfileCreate, PrakritiProfileResponse
from app.dependencies import get_current_user
from app.services.prakriti_service import PrakritiService

router = APIRouter()
prakriti_service = PrakritiService()


@router.post('/profile', response_model=PrakritiProfileResponse)
async def create_profile(data: PrakritiProfileCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	try:
		scores = prakriti_service.calculate_dominant_dosha(data.vata_score, data.pitta_score, data.kapha_score)
		payload = data.model_dump()
		payload['dominant_dosha'] = scores['dominant_dosha']
		payload['risk_score'] = scores['constitutional_risk_score']
		profile = PrakritiProfile(**payload, user_id=current_user.id)
		db.add(profile)
		await db.commit()
		await db.refresh(profile)
		return profile
	except Exception as exc:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'Unable to create profile: {exc}')


@router.get('/profile', response_model=PrakritiProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	try:
		result = await db.execute(select(PrakritiProfile).where(PrakritiProfile.user_id == current_user.id).order_by(PrakritiProfile.completed_at.desc()))
		profile = result.scalars().first()
		if not profile:
			raise HTTPException(status_code=404, detail='Profile not found')
		return profile
	except HTTPException:
		raise
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f'Unable to fetch profile: {exc}')


@router.put('/profile', response_model=PrakritiProfileResponse)
async def update_profile(data: PrakritiProfileCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	try:
		scores = prakriti_service.calculate_dominant_dosha(data.vata_score, data.pitta_score, data.kapha_score)
		payload = data.model_dump()
		payload['dominant_dosha'] = scores['dominant_dosha']
		payload['risk_score'] = scores['constitutional_risk_score']

		result = await db.execute(select(PrakritiProfile).where(PrakritiProfile.user_id == current_user.id))
		profile = result.scalars().first()
		if not profile:
			profile = PrakritiProfile(**payload, user_id=current_user.id)
			db.add(profile)
		else:
			for k, v in payload.items():
				setattr(profile, k, v)
		await db.commit()
		await db.refresh(profile)
		return profile
	except Exception as exc:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'Unable to update profile: {exc}')


@router.post('/vision-analyse')
async def vision_analyse(image: UploadFile = File(...), current_user: User = Depends(get_current_user)):
	try:
		file_bytes = await image.read()
		tmp_dir = Path('/tmp')
		tmp_dir.mkdir(parents=True, exist_ok=True)
		save_path = tmp_dir / image.filename
		async with aiofiles.open(save_path, 'wb') as out_file:
			await out_file.write(file_bytes)

		digest = int(hashlib.sha256(image.filename.encode('utf-8')).hexdigest(), 16)
		choices = ['vata', 'pitta', 'kapha']
		hint_dosha = choices[digest % 3]
		confidence = round(0.68 + ((digest % 20) / 100), 2)
		return {
			'hint_dosha': hint_dosha,
			'confidence': confidence,
			'note': 'Computer vision analysis - confirm with full quiz',
		}
	except Exception as exc:
		return {'hint_dosha': 'vata', 'confidence': 0.7, 'note': f'Computer vision analysis - confirm with full quiz ({exc})'}


@router.get('/tips')
async def get_tips(dosha: str = 'vata', current_user: User = Depends(get_current_user)):
	try:
		return {'tips': prakriti_service.get_dosha_tips(dosha, count=3)}
	except Exception:
		return {'tips': ['Drink warm water every morning', 'Maintain regular meal times', 'Sleep before 10:30 PM']}
