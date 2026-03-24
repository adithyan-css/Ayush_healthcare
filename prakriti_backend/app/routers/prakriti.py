from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.prakriti import PrakritiProfile
from app.schemas.schemas import PrakritiProfileCreate, PrakritiProfileResponse
from app.dependencies import get_current_user

router = APIRouter()


@router.post('/profile', response_model=PrakritiProfileResponse)
async def create_profile(data: PrakritiProfileCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	profile = PrakritiProfile(**data.model_dump(), user_id=current_user.id)
	db.add(profile)
	await db.commit()
	await db.refresh(profile)
	return profile


@router.get('/profile', response_model=PrakritiProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(PrakritiProfile).where(PrakritiProfile.user_id == current_user.id).order_by(PrakritiProfile.completed_at.desc()))
	profile = result.scalars().first()
	if not profile:
		raise HTTPException(status_code=404, detail='Profile not found')
	return profile


@router.put('/profile', response_model=PrakritiProfileResponse)
async def update_profile(data: PrakritiProfileCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	result = await db.execute(select(PrakritiProfile).where(PrakritiProfile.user_id == current_user.id))
	profile = result.scalars().first()
	if not profile:
		profile = PrakritiProfile(**data.model_dump(), user_id=current_user.id)
		db.add(profile)
	else:
		for k, v in data.model_dump().items():
			setattr(profile, k, v)
	await db.commit()
	await db.refresh(profile)
	return profile


@router.post('/vision-analyse')
async def vision_analyse(current_user: User = Depends(get_current_user)):
	return {'dosha': 'Pitta', 'confidence': 0.85, 'note': 'Vision analysis requires google_ml_kit integration on device'}


@router.get('/tips')
async def get_tips(dosha: str = 'vata', current_user: User = Depends(get_current_user)):
	tips = {
		'vata': ['Drink warm water every morning', 'Avoid cold and dry foods', 'Maintain a regular daily routine'],
		'pitta': ['Favor cooling foods like cucumber', 'Avoid excessive spicy food', 'Practice cooling pranayama'],
		'kapha': ['Exercise daily in the morning', 'Avoid heavy oily foods', 'Favor light warm spiced meals']
	}
	return {'tips': tips.get(dosha.lower(), tips['vata'])}
