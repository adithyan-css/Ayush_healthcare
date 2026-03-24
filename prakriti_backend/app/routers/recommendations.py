from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.prakriti import PrakritiProfile
from app.models.recommendation import RecommendationSession
from app.schemas.schemas import RecommendationRequest, RecommendationSessionResponse
from app.dependencies import get_current_user
from app.services.recommendation_service import RecommendationService
from app.services.weather_service import WeatherService

router = APIRouter()
recommendation_service = RecommendationService()
ws = WeatherService()


@router.post('/generate', response_model=RecommendationSessionResponse)
async def generate(req: RecommendationRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	try:
		p_result = await db.execute(select(PrakritiProfile).where(PrakritiProfile.user_id == current_user.id).order_by(PrakritiProfile.completed_at.desc()))
		profile = p_result.scalars().first()
		dosha = profile.dominant_dosha if profile else 'vata'
		vata = (profile.vata_score * 10) if profile else 33
		pitta = (profile.pitta_score * 10) if profile else 33
		kapha = (profile.kapha_score * 10) if profile else 34

		s_result = await db.execute(select(RecommendationSession).where(RecommendationSession.user_id == current_user.id).order_by(RecommendationSession.created_at.desc()).limit(3))
		history = s_result.scalars().all()
		history_data = [
			{
				'date': str(h.created_at.date()),
				'symptoms': h.symptoms if isinstance(h.symptoms, list) else h.symptoms.get('items', []),
			}
			for h in history
		]
		season = ws.get_current_season()
		free_text = req.free_text
		if req.variation:
			suffix = ', please vary the suggestions from previous recommendations'
			free_text = (free_text or '') + suffix

		ai_response = await recommendation_service.generate_recommendation(dosha, vata, pitta, kapha, season, req.symptoms, history_data, free_text, current_user.language)
		session = RecommendationSession(
			user_id=current_user.id,
			symptoms={'items': req.symptoms},
			season=season,
			free_text=free_text,
			response_json=ai_response,
			prevention_plan=ai_response.get('prevention_30day', ''),
		)
		db.add(session)
		await db.commit()
		await db.refresh(session)
		return session
	except Exception as exc:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'Unable to generate recommendation: {exc}')


@router.get('/history')
async def get_history(page: int = 1, limit: int = 10, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	try:
		offset = (page - 1) * limit
		result = await db.execute(select(RecommendationSession).where(RecommendationSession.user_id == current_user.id).order_by(RecommendationSession.created_at.desc()).offset(offset).limit(limit))
		sessions = result.scalars().all()
		for session in sessions:
			if isinstance(session.symptoms, dict):
				session.symptoms = session.symptoms.get('items', [])
		return sessions
	except Exception:
		return []


@router.get('/{id}', response_model=RecommendationSessionResponse)
async def get_rec(id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	try:
		result = await db.execute(select(RecommendationSession).where(RecommendationSession.id == id, RecommendationSession.user_id == current_user.id))
		session = result.scalars().first()
		if not session:
			raise HTTPException(status_code=404)
		if isinstance(session.symptoms, dict):
			session.symptoms = session.symptoms.get('items', [])
		return session
	except HTTPException:
		raise
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f'Unable to load recommendation: {exc}')


@router.delete('/{id}')
async def delete_rec(id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	try:
		result = await db.execute(select(RecommendationSession).where(RecommendationSession.id == id, RecommendationSession.user_id == current_user.id))
		session = result.scalars().first()
		if not session:
			raise HTTPException(status_code=404)
		await db.delete(session)
		await db.commit()
		return {'status': 'deleted'}
	except HTTPException:
		raise
	except Exception as exc:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f'Unable to delete recommendation: {exc}')


@router.post('/prevention')
async def prevention(data: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
	location = data.get('location', 'India')
	risk_score = int(data.get('risk_score', 50))
	age_group = data.get('age_group', 'adult')
	dosha = data.get('dosha', 'vata')
	try:
		profile_res = await db.execute(select(PrakritiProfile).where(PrakritiProfile.user_id == current_user.id).order_by(PrakritiProfile.completed_at.desc()))
		profile = profile_res.scalars().first()
		if profile:
			dosha = profile.dominant_dosha
		plan = recommendation_service.generate_prevention_plan(location=location, risk_score=risk_score, dosha=dosha, season=ws.get_current_season())
		return {'plan': plan}
	except Exception:
		return {
			'plan': f'30-day prevention plan for {location}: maintain regular sleep, follow dosha-balanced diet for {dosha}, use daily pranayama, and monitor weekly risk at {risk_score}/100.'
		}
